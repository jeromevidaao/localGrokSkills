#!/usr/bin/env bash
# Idempotent post-"Update Grok Bot's Computer" restore for shared Linux box.
# Reinstalls CLIs that do NOT survive Update; reuses persisted ~/.aws ~/.grok files.
# Never prints access keys / secrets.
set -euo pipefail

PASS=0
FAIL=0
WARN=0
NOTES=()

ok()   { echo "PASS  $*"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $*"; FAIL=$((FAIL+1)); }
warn() { echo "WARN  $*"; WARN=$((WARN+1)); NOTES+=("$*"); }
info() { echo "INFO  $*"; }

HOME_DIR="${HOME:-/home/box}"
LOCAL_BIN="$HOME_DIR/.local/bin"
GROK_BIN="$HOME_DIR/.grok/bin"
AWS_VENV="$HOME_DIR/.local/awscli-venv"
AWS_PROFILE_NAME="grok-bot-titan"
AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
AWS_ACCOUNT_EXPECT="834917996497"
SKILLS_REPO_URL="https://github.com/jeromevidaao/localGrokSkills.git"
SKILLS_CLONE="${LOCALGROK_SKILLS_ROOT:-/workspace/localGrokSkills}"
SSM_KEY_ID_NAME="/grok/titan-iam-access-key-id"
SSM_SECRET_NAME="/grok/titan-iam-secret-access-key"

export PATH="$LOCAL_BIN:$GROK_BIN:$PATH"

echo "=== box-bootstrap: restore CLIs after Update Computer ==="
echo "time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo

# ---------- PATH ----------
ensure_path_line() {
  local line="$1" file="$2"
  mkdir -p "$(dirname "$file")"
  touch "$file"
  if ! grep -Fqx "$line" "$file" 2>/dev/null; then
    printf '\n%s\n' "$line" >> "$file"
  fi
}
mkdir -p "$LOCAL_BIN" "$GROK_BIN"
ensure_path_line 'export PATH="$HOME/.local/bin:$PATH"' "$HOME_DIR/.bashrc"
ensure_path_line 'export PATH="$HOME/.grok/bin:$PATH"' "$HOME_DIR/.bashrc"
ok "PATH includes ~/.local/bin and ~/.grok/bin (session + ~/.bashrc)"

# ---------- AWS CLI (match box: pip awscli in user venv → ~/.local/bin/aws) ----------
install_aws_cli() {
  info "Installing/updating AWS CLI via python venv at $AWS_VENV"
  if [[ ! -x "$AWS_VENV/bin/python" ]]; then
    python3 -m venv "$AWS_VENV"
  fi
  # shellcheck disable=SC1091
  "$AWS_VENV/bin/pip" install -q --upgrade pip
  "$AWS_VENV/bin/pip" install -q --upgrade 'awscli>=1.32'
  ln -sfn "$AWS_VENV/bin/aws" "$LOCAL_BIN/aws"
}

if command -v aws >/dev/null 2>&1 && aws --version >/dev/null 2>&1; then
  info "aws already runnable: $(aws --version 2>&1 | head -1)"
  # Ensure symlink/venv still the expected layout; repair if broken
  if [[ ! -x "$LOCAL_BIN/aws" ]]; then
    install_aws_cli
  fi
else
  install_aws_cli
fi

if command -v aws >/dev/null 2>&1 && aws --version >/dev/null 2>&1; then
  ok "aws CLI: $(aws --version 2>&1 | head -1)"
else
  bad "aws CLI not runnable after install"
fi

# ---------- AWS credentials / profile (reuse files; SSM only if needed) ----------
mkdir -p "$HOME_DIR/.aws"
chmod 700 "$HOME_DIR/.aws" 2>/dev/null || true
[[ -f "$HOME_DIR/.aws/credentials" ]] && chmod 600 "$HOME_DIR/.aws/credentials" || true
[[ -f "$HOME_DIR/.aws/config" ]] && chmod 600 "$HOME_DIR/.aws/config" || true

# Ensure config has default + named profile region (no secrets)
aws_config_ensure() {
  local cfg="$HOME_DIR/.aws/config"
  touch "$cfg"
  chmod 600 "$cfg"
  if ! grep -qE '^\[default\]' "$cfg" 2>/dev/null; then
    printf '[default]\nregion = %s\noutput = json\n\n' "$AWS_REGION" >> "$cfg"
  fi
  if ! grep -qE "^\[profile ${AWS_PROFILE_NAME}\]" "$cfg" 2>/dev/null; then
    printf '[profile %s]\nregion = %s\noutput = json\n\n' "$AWS_PROFILE_NAME" "$AWS_REGION" >> "$cfg"
  fi
}
aws_config_ensure

sts_ok() {
  local profile_args=()
  if [[ -n "${1:-}" ]]; then
    profile_args=(--profile "$1")
  fi
  aws "${profile_args[@]}" sts get-caller-identity --query Account --output text 2>/dev/null | grep -qx "$AWS_ACCOUNT_EXPECT"
}

# Copy keys from one profile to another without printing values
copy_profile_keys() {
  local src="$1" dst="$2"
  local kid sec
  if [[ "$src" == "default" || -z "$src" ]]; then
    kid="$(aws configure get aws_access_key_id 2>/dev/null || true)"
    sec="$(aws configure get aws_secret_access_key 2>/dev/null || true)"
  else
    kid="$(aws configure get aws_access_key_id --profile "$src" 2>/dev/null || true)"
    sec="$(aws configure get aws_secret_access_key --profile "$src" 2>/dev/null || true)"
  fi
  if [[ -z "$kid" || -z "$sec" ]]; then
    return 1
  fi
  aws configure set aws_access_key_id "$kid" --profile "$dst"
  aws configure set aws_secret_access_key "$sec" --profile "$dst"
  aws configure set region "$AWS_REGION" --profile "$dst"
  chmod 600 "$HOME_DIR/.aws/credentials"
  return 0
}

fetch_ssm_into_profile() {
  # Requires SOME working AWS identity already (chicken-egg: Update keeps ~/.aws).
  local kid sec
  info "Fetching IAM keys from SSM into profile $AWS_PROFILE_NAME (values not printed)"
  kid="$(aws ssm get-parameter --name "$SSM_KEY_ID_NAME" --with-decryption --query Parameter.Value --output text 2>/dev/null || true)"
  sec="$(aws ssm get-parameter --name "$SSM_SECRET_NAME" --with-decryption --query Parameter.Value --output text 2>/dev/null || true)"
  if [[ -z "$kid" || -z "$sec" || "$kid" == "None" || "$sec" == "None" ]]; then
    return 1
  fi
  aws configure set aws_access_key_id "$kid" --profile "$AWS_PROFILE_NAME"
  aws configure set aws_secret_access_key "$sec" --profile "$AWS_PROFILE_NAME"
  aws configure set region "$AWS_REGION" --profile "$AWS_PROFILE_NAME"
  # Also keep [default] usable for scripts that omit --profile
  aws configure set aws_access_key_id "$kid"
  aws configure set aws_secret_access_key "$sec"
  aws configure set region "$AWS_REGION"
  chmod 600 "$HOME_DIR/.aws/credentials"
  return 0
}

AWS_IDENTITY_OK=0
if sts_ok; then
  AWS_IDENTITY_OK=1
  info "default/env STS identity OK (account $AWS_ACCOUNT_EXPECT)"
elif sts_ok "$AWS_PROFILE_NAME"; then
  AWS_IDENTITY_OK=1
  info "profile $AWS_PROFILE_NAME STS identity OK"
fi

if [[ "$AWS_IDENTITY_OK" -eq 1 ]]; then
  # Ensure named profile exists for callers that use --profile grok-bot-titan
  if ! sts_ok "$AWS_PROFILE_NAME"; then
    if copy_profile_keys default "$AWS_PROFILE_NAME" || copy_profile_keys "" "$AWS_PROFILE_NAME"; then
      info "Mirrored working keys into profile $AWS_PROFILE_NAME"
    fi
  fi
  if sts_ok "$AWS_PROFILE_NAME" || sts_ok; then
    ARN="$(aws sts get-caller-identity --query Arn --output text 2>/dev/null || aws --profile "$AWS_PROFILE_NAME" sts get-caller-identity --query Arn --output text 2>/dev/null || echo unknown)"
    ok "AWS STS: $ARN"
  else
    bad "AWS STS: could not finalize profile $AWS_PROFILE_NAME"
  fi
else
  # No working identity. Try SSM only if some ambient creds exist (unlikely) —
  # otherwise document chicken-egg: Update Computer keeps ~/.aws; Reset would wipe it.
  if fetch_ssm_into_profile && (sts_ok "$AWS_PROFILE_NAME" || sts_ok); then
    ARN="$(aws --profile "$AWS_PROFILE_NAME" sts get-caller-identity --query Arn --output text 2>/dev/null || echo unknown)"
    ok "AWS STS via SSM restore: $ARN"
  else
    bad "AWS STS: no valid credentials. Update Computer normally keeps ~/.aws — if missing, restore keys manually (SSM $SSM_KEY_ID_NAME / $SSM_SECRET_NAME) then re-run. Do NOT use Reset Computer."
  fi
fi

# ---------- grok CLI ----------
install_grok() {
  info "Installing/updating grok CLI via https://x.ai/cli/install.sh"
  curl -fsSL https://x.ai/cli/install.sh | bash
}

if command -v grok >/dev/null 2>&1; then
  if grok update >/dev/null 2>&1 || true; then
    :
  fi
  # If still broken, reinstall
  if ! grok --version >/dev/null 2>&1; then
    install_grok
  fi
else
  install_grok
fi

if command -v grok >/dev/null 2>&1 && grok --version >/dev/null 2>&1; then
  ok "grok CLI: $(grok --version 2>&1 | head -1)"
else
  bad "grok CLI not runnable (tried curl -fsSL https://x.ai/cli/install.sh | bash)"
fi

# ---------- localGrokSkills + ~/.grok/skills symlink ----------
ensure_skills_repo() {
  if [[ -d "$SKILLS_CLONE/.git" ]]; then
    info "git pull --ff-only in $SKILLS_CLONE"
    git -C "$SKILLS_CLONE" pull --ff-only || warn "git pull failed in $SKILLS_CLONE (network/auth?); continuing with existing clone"
  else
    info "Cloning $SKILLS_REPO_URL → $SKILLS_CLONE"
    mkdir -p "$(dirname "$SKILLS_CLONE")"
    if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
      gh repo clone jeromevidaao/localGrokSkills "$SKILLS_CLONE" || git clone "$SKILLS_REPO_URL" "$SKILLS_CLONE"
    else
      git clone "$SKILLS_REPO_URL" "$SKILLS_CLONE"
    fi
  fi
  if [[ -x "$SKILLS_CLONE/install.sh" ]]; then
    bash "$SKILLS_CLONE/install.sh"
  else
    mkdir -p "$HOME_DIR/.grok"
    ln -sfn "$SKILLS_CLONE/skills" "$HOME_DIR/.grok/skills"
  fi
}

ensure_skills_repo

SKILLS_LINK="$HOME_DIR/.grok/skills"
if [[ -L "$SKILLS_LINK" ]]; then
  TARGET="$(readlink -f "$SKILLS_LINK" 2>/dev/null || readlink "$SKILLS_LINK")"
  if [[ -d "$TARGET" ]] && [[ -f "$TARGET/r2-memory/SKILL.md" || -d "$TARGET/r2-memory" ]]; then
    ok "skills link: $SKILLS_LINK → $TARGET"
  else
    bad "skills link exists but target missing expected skills: $TARGET"
  fi
elif [[ -d "$SKILLS_LINK" ]]; then
  warn "skills is a directory, not symlink: $SKILLS_LINK (install.sh should have fixed)"
  ok "skills directory present at $SKILLS_LINK"
else
  bad "~/.grok/skills missing after install"
fi

# ---------- gh auth (non-secret check only) ----------
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    ok "gh auth: logged in ($(gh api user -q .login 2>/dev/null || echo ok))"
  else
    warn "gh present but not authenticated — user must run: gh auth login"
  fi
else
  warn "gh not installed — install via apt/official method if needed; then gh auth login"
fi

# ---------- optional: ensure ~/.grok/bin on path for non-interactive ----------
if [[ -x "$GROK_BIN/grok" ]] && [[ ! -e /usr/local/bin/grok ]]; then
  # do not require root; PATH already handled
  :
fi

# ---------- Checklist summary ----------
echo
echo "=== CHECKLIST ==="
echo "PASS=$PASS  FAIL=$FAIL  WARN=$WARN"
if [[ "$FAIL" -eq 0 ]]; then
  echo "RESULT: ALL CRITICAL CHECKS PASSED"
  echo
  echo "After Update Computer, re-run:"
  echo "  bash ~/.grok/skills/box-bootstrap/scripts/bootstrap_box_clis.sh"
  echo
  echo "Chicken-egg: Update keeps ~/.aws and ~/.grok files; only apt/pip/CLI binaries vanish."
  echo "If ~/.aws was wiped (e.g. Reset — avoid), restore keys then re-run."
  exit 0
else
  echo "RESULT: SOME CHECKS FAILED — see FAIL lines above"
  for n in "${NOTES[@]:-}"; do echo "NOTE: $n"; done
  exit 1
fi
