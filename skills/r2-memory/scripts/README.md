# Local R2Memory + Titan (full potential)

Parity with `lib/chat-memory.js` + Grok skill workflow.

| Script | Role |
|--------|------|
| `r2_memory_bootstrap.py` | Session start: pull + standing retrieve + decisions |
| `r2_memory_gate.py` | **Mandatory** pre-answer gate |
| `r2_retrieve.py` | Keyword + Titan search (3 indexes) |
| `r2_memory_turn.py` | Buffer / chitchat skip / dual-write / auto-flush |
| `r2_titan_lib.py` | Shared library |

Mirror into `~/.grok/skills/r2-memory/scripts/` when editing.

Default embed: **exchange-only** (`R2_MEMORY_EMBED_MODE=exchange`).  
Default flush every **3** turns.  
Unified prefs index: **`chat_agent_ops`**.
