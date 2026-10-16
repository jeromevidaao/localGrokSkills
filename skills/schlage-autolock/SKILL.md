---
name: schlage-autolock
description: >-
  Use for the hourly autolockSchlage Lambda (us-east-1) that force-locks Schlage
  WiFi doors left open >15 min and alerts SNS autolockSchlage-alerts.
---
# autolockSchlage

- Repo: github.com/jeromevidaao/autolock-schlage (checkout /tmp/autolock-schlage). Deploy = CI on main → Deploy workflow; if CI's artifact upload hits quota, run `gh workflow run deploy.yml --ref main` (it builds its own zip).
- Creds: SSM SecureString `/schlage/email`, `/schlage/password` (fetch at runtime, never print).
- Read-only check: invoke with `{"action":"check"}` → dry run, returns `would_lock`, never locks/unlocks, no SNS.
- **Settle re-check (2d8e7ba, 2026-10-16):** after 3 lock tries, wait `LOCK_SETTLE_RECHECK_SEC` (15 s) and refresh once more before a "still unlocked" alert. Schlage state lags the bolt; Apt #2 back false alarms at 6:56/11:56 AM PT were locked ~2 s after we gave up. Tests: test_lock_settle.py.
- Versions: v1 = rollback (043c794, pre-fix); v2 = 2d8e7ba. Rollback: `aws lambda update-function-code` from v1 zip or redeploy 043c794.
- Hardcoded door PINs are NOT in this Lambda; PERMANENT_CODES (Richard/Jerome/Cleaning) live in addDeleteCodeWiFiPyschlage lambda_function.py — SSM move pending Jerome's OK on that Lambda.
