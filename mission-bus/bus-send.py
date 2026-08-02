#!/usr/bin/env python3
"""Post a Mission Bus message from Cloud Ren (or any node).

Usage:
  python mission-bus/bus-send.py --from cloud --to laptop --kind handshake "hello"
  python mission-bus/bus-send.py --from laptop --to cloud --kind reply --re ID "ack"
"""

from __future__ import annotations

import argparse
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUS = ROOT / "mission-bus"


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="frm", required=True, choices=["cloud", "laptop", "grok"])
    p.add_argument("--to", dest="to", required=True, choices=["cloud", "laptop", "grok"])
    p.add_argument("--kind", default="note")
    p.add_argument("--re", dest="re_id", default=None)
    p.add_argument("--status", default="open")
    p.add_argument("body", nargs=argparse.REMAINDER)
    args = p.parse_args()
    body = " ".join(args.body).strip()
    if not body:
        raise SystemExit("body required")

    lanes = {
        ("cloud", "laptop"): BUS / "cloud-to-laptop",
        ("laptop", "cloud"): BUS / "laptop-to-cloud",
        ("laptop", "grok"): BUS / "laptop-to-grok",
        ("grok", "laptop"): BUS / "grok-to-laptop",
    }
    folder = lanes.get((args.frm, args.to))
    if folder is None:
        raise SystemExit("unsupported lane — use cloud↔laptop or laptop↔grok")

    folder.mkdir(parents=True, exist_ok=True)
    msg_id = str(uuid.uuid4())
    slug = re.sub(r"[^a-z0-9]+", "-", body.lower())[:40].strip("-") or "msg"
    path = folder / f"{stamp()}-{args.frm}-{slug}.md"
    lines = [
        "---",
        f"id: {msg_id}",
        f"from: {args.frm}",
        f"to: {args.to}",
        f"created: {iso_now()}",
        f"kind: {args.kind}",
        f"status: {args.status}",
    ]
    if args.re_id:
        lines.append(f"re: {args.re_id}")
    lines.extend(["---", "", body, ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    print(path)
    print(msg_id)


if __name__ == "__main__":
    main()
