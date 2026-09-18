# HARD — harness prepush before push

Before `git push` on `auto-reply-sqs-harness` (guest auto-reply, goldens, eval, prompts, `src/agent.js`, tools):

1. Load skill **`guest-messaging-harness`**.
2. Run `python3 ~/.grok/skills/guest-messaging-harness/scripts/prepush.py` (or `npm run prepush` in that repo).
3. **Do not push** if phrase-check, `npm test`, or live eval is red.

CI eval must not be the first time new `requiredPhrases` or category rubrics are tested. Local suite first, full eval, no `--fail-fast`.

4. After any CI fail: fix locally, re-run the **exact** failing eval/test (`npm run eval -- --only=<id>`) until green, then push. Never push on red.
5. Credential/WiFi/SSID policy changes: update **all** goldens that assert SSID/password phrases in the same PR (see skill `guest-messaging-harness` § Credential / WiFi / SSID golden sync).
