# James-Ren

Home base for **Ren** + James.

## Defaults
See `ren/JAMES-DEFAULTS.md` — Taiwan / **NTD** (SGD otherwise), 光華 for local street checks.

## Mission Bus (Cloud Ren ↔ Laptop Ren)

Shared mailbox in git. Auto-sync stays **OFF**.

**On the Acer (Laptop Ren):**

```bash
git pull
python mission-bus/sync-bus.py
python mission-bus/sync-bus.py --ack <id> "laptop Ren online" --push
python mission-bus/sync-bus.py --send "yo cloud" --push
```

Details: `mission-bus/PROTOCOL.md`

## Telegram note

Telegram text can reach Cloud Ren. Replies and images don’t reliably come back through Telegram yet — use Mission Bus + this GitHub repo / Cursor agent thread for the return path.
