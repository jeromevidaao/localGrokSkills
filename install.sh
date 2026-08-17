#!/usr/bin/env bash
# Wire this clone into $GROK_HOME so Grok loads these skills and sync hooks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GROK_HOME="${GROK_HOME:-$HOME/.grok}"

mkdir -p "$GROK_HOME/hooks/bin" "$GROK_HOME/rules"

# Skills: replace a real directory with a symlink (keep a dated backup).
if [ -L "$GROK_HOME/skills" ]; then
  ln -sfn "$ROOT/skills" "$GROK_HOME/skills"
elif [ -d "$GROK_HOME/skills" ]; then
  bak="$GROK_HOME/skills.bak.$(date +%Y%m%d%H%M%S)"
  mv "$GROK_HOME/skills" "$bak"
  ln -sfn "$ROOT/skills" "$GROK_HOME/skills"
  echo "Backed up existing skills to $bak"
else
  ln -sfn "$ROOT/skills" "$GROK_HOME/skills"
fi

# Home rules (always loaded)
for f in "$ROOT/grok-rules/"*.md; do
  [ -f "$f" ] || continue
  ln -sfn "$f" "$GROK_HOME/rules/$(basename "$f")"
done

# Existing always-push Stop gate
ln -sfn "$ROOT/scripts/stop-always-push.py" "$GROK_HOME/hooks/bin/stop-always-push.py"
ln -sfn "$ROOT/grok-hooks/always-commit-push.json" "$GROK_HOME/hooks/always-commit-push.json"

# Launch pull + dirty-tree commit/push (absolute paths; ~ is not expanded by hooks)
cat > "$GROK_HOME/hooks/local-grok-skills.json" <<EOF
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${ROOT}/scripts/sync.py pull && python3 ${ROOT}/scripts/health_skills.py",
            "timeout": 45
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${ROOT}/scripts/sync.py commit-push",
            "timeout": 300
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${ROOT}/scripts/sync.py commit-push",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
EOF

chmod +x "$ROOT/install.sh" "$ROOT/scripts/"*.py "$ROOT/scripts/"*.sh 2>/dev/null || true

echo "localGrokSkills installed"
echo "  skills: $GROK_HOME/skills -> $ROOT/skills"
echo "  hooks:  SessionStart pull, Stop/SessionEnd commit-push"
echo "  rules:  $GROK_HOME/rules/"
