#!/usr/bin/env python3
"""Mission Bus sync for Laptop Ren (main Ren on Acer).

Manual by default (auto-sync OFF). Pulls cloud→laptop mail, can post
laptop→cloud replies, updates laptop status heartbeat.

Usage (from repo root, on the laptop):
  python mission-bus/sync-bus.py              # pull + list open mail
  python mission-bus/sync-bus.py --pull      # git pull only + list
  python mission-bus/sync-bus.py --ack ID "got it"
  python mission-bus/sync-bus.py --send "yo cloud, laptop online"
  python mission-bus/sync-bus.py --watch     # poll every 30s (only if James says so)
  python mission-bus/sync-bus.py --push      # commit+push status/outbox changes
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUS = ROOT / "mission-bus"
INBOX = BUS / "cloud-to-laptop"
OUTBOX = BUS / "laptop-to-cloud"
STATUS_LAPTOP = BUS / "status" / "laptop.json"
STATUS_CLOUD = BUS / "status" / "cloud.json"

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stamp() -> str:
    return utc_now().strftime("%Y%m%d-%H%M%SZ")


def iso_now() -> str:
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def git_pull() -> None:
    try:
        r = run(["git", "pull", "--ff-only", "origin", "HEAD"], check=False)
        if r.returncode != 0:
            # fallback: pull current branch from origin
            branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            r2 = run(["git", "pull", "--ff-only", "origin", branch], check=False)
            print(r2.stdout or r2.stderr)
        else:
            print(r.stdout or "pulled")
    except Exception as e:
        print(f"pull failed: {e}", file=sys.stderr)


def git_push() -> None:
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    run(["git", "add", "mission-bus"])
    status = run(["git", "status", "--porcelain", "mission-bus"]).stdout.strip()
    if not status:
        print("nothing to push")
        return
    msg = f"mission-bus: laptop sync {iso_now()}"
    run(["git", "commit", "-m", msg])
    r = run(["git", "push", "-u", "origin", branch], check=False)
    print(r.stdout or r.stderr)
    if r.returncode != 0:
        sys.exit(r.returncode)


def parse_message(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    meta: dict[str, str] = {}
    body = text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2).strip()
    return {"path": path, "meta": meta, "body": body}


def list_messages(folder: Path) -> list[dict]:
    if not folder.exists():
        return []
    msgs = []
    for p in sorted(folder.glob("*.md")):
        if p.name.upper() == "README.MD":
            continue
        msgs.append(parse_message(p))
    return msgs


def print_inbox() -> None:
    msgs = list_messages(INBOX)
    open_msgs = [m for m in msgs if m["meta"].get("status", "open") == "open"]
    print(f"\n=== cloud → laptop ({len(open_msgs)} open / {len(msgs)} total) ===")
    if not msgs:
        print("(empty)")
        return
    for m in msgs:
        meta = m["meta"]
        flag = meta.get("status", "open")
        print(
            f"- [{flag}] {meta.get('id', '?')} | {meta.get('kind', 'note')} | "
            f"{meta.get('created', '?')}\n  {m['path'].name}\n  {m['body'][:160]}"
        )


def print_cloud_status() -> None:
    print("\n=== cloud status ===")
    if not STATUS_CLOUD.exists():
        print("(no cloud status yet)")
        return
    data = json.loads(STATUS_CLOUD.read_text(encoding="utf-8"))
    for k, v in data.items():
        print(f"  {k}: {v}")


def bump_laptop_status(note: str | None = None) -> None:
    data = {
        "node": "laptop",
        "agent": "main-ren",
        "host": "acer",
        "last_seen": iso_now(),
        "notes": note or "Laptop Ren synced Mission Bus.",
    }
    STATUS_LAPTOP.parent.mkdir(parents=True, exist_ok=True)
    STATUS_LAPTOP.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"updated {STATUS_LAPTOP.relative_to(ROOT)}")


def write_outbox(
    body: str,
    *,
    kind: str = "note",
    re_id: str | None = None,
    status: str = "open",
) -> Path:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    msg_id = str(uuid.uuid4())
    slug = re.sub(r"[^a-z0-9]+", "-", body.lower())[:40].strip("-") or "msg"
    path = OUTBOX / f"{stamp()}-laptop-{slug}.md"
    lines = [
        "---",
        f"id: {msg_id}",
        "from: laptop",
        "to: cloud",
        f"created: {iso_now()}",
        f"kind: {kind}",
        f"status: {status}",
    ]
    if re_id:
        lines.append(f"re: {re_id}")
    lines.extend(["---", "", body.strip(), ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")
    return path


def ack(msg_id: str, body: str) -> None:
    write_outbox(body, kind="reply", re_id=msg_id, status="open")
    # mark original as acked if found
    for m in list_messages(INBOX):
        if m["meta"].get("id") == msg_id:
            text = m["path"].read_text(encoding="utf-8")
            text2 = re.sub(
                r"(?m)^status:\s*\w+",
                "status: acked",
                text,
                count=1,
            )
            m["path"].write_text(text2, encoding="utf-8")
            print(f"acked inbox {m['path'].name}")
            break
    else:
        print(f"warning: no inbox message with id {msg_id}", file=sys.stderr)


def once(do_pull: bool) -> None:
    if do_pull:
        git_pull()
    bump_laptop_status()
    print_cloud_status()
    print_inbox()


def main() -> None:
    p = argparse.ArgumentParser(description="Mission Bus sync (laptop Ren)")
    p.add_argument("--pull", action="store_true", help="git pull before listing")
    p.add_argument("--push", action="store_true", help="commit+push mission-bus changes")
    p.add_argument("--send", metavar="TEXT", help="post laptop→cloud note")
    p.add_argument("--ack", nargs=2, metavar=("ID", "TEXT"), help="reply to cloud message id")
    p.add_argument(
        "--watch",
        action="store_true",
        help="poll every 30s (OFF by default; only if James asks)",
    )
    p.add_argument("--interval", type=int, default=30, help="watch interval seconds")
    args = p.parse_args()

    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)

    if args.send:
        if args.pull:
            git_pull()
        write_outbox(args.send, kind="note")
        bump_laptop_status("Laptop Ren sent a bus message.")
        if args.push:
            git_push()
        return

    if args.ack:
        if args.pull:
            git_pull()
        ack(args.ack[0], args.ack[1])
        bump_laptop_status("Laptop Ren acked a cloud message.")
        if args.push:
            git_push()
        return

    if args.watch:
        print("watch mode ON — Ctrl+C to stop (auto-sync is normally OFF)")
        while True:
            once(do_pull=True)
            if args.push:
                git_push()
            time.sleep(max(5, args.interval))

    once(do_pull=args.pull or True)
    if args.push:
        git_push()


if __name__ == "__main__":
    main()
