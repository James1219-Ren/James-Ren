# Mission Bus protocol

Shared mailbox via **this git repo**.

Originally: **Cloud Ren** ↔ **Laptop Ren**.  
Extended: **Laptop Ren → Grok** (Grok reads via GitHub connector after push).

## Folders

| Path | Who writes | Who reads |
|------|------------|-----------|
| `mission-bus/cloud-to-laptop/` | Cloud Ren | Laptop Ren |
| `mission-bus/laptop-to-cloud/` | Laptop Ren | Cloud Ren |
| `mission-bus/laptop-to-grok/` | Laptop Ren | Grok (GitHub connector) |
| `mission-bus/grok-to-laptop/` | Grok (only if James OK) | Laptop Ren |
| `mission-bus/status/` | Either | Either |

## Message file format

Filename: `YYYYMMDD-HHMMSSZ-<from>-<slug>.md`

Front matter (first lines):

```
---
id: <uuid>
from: cloud|laptop|grok
to: laptop|cloud|grok
created: <ISO-8601 UTC>
kind: note|task|reply|handshake|image-note
re: <optional parent id>
status: open|acked|done
---

Body in plain language.
```

## Rules

1. **Never** put secrets, tokens, `.env`, or classified Alicia lore on the bus.
2. Auto-sync stays **OFF**. Laptop Ren runs `python mission-bus/sync-bus.py` when James asks (or watches with `--watch`).
3. Ack important messages by writing a `kind: reply` with `re: <id>`.
4. Images: if Telegram/cloud cannot carry the file, drop an `image-note` describing what was sent + where the file lives on the device.
5. Keep bodies short. James is non-technical — write like Ren talking to Ren, not a ticket system.
6. **Grok lane:** Laptop Ren may push timestamped notes to `laptop-to-grok/`. Grok reads after push; Grok does **not** push/write back unless James explicitly says OK. Drive `_relay/to-grok/` / `from-grok/` remains a secondary channel.
