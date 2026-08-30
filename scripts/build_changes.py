#!/usr/bin/env python3
"""Write the day's added/removed diff for the mirrored feed.

The mirror commits a snapshot every 6 hours, so `git log -p feed.txt` already
holds this information - but only as a diff you have to reconstruct, against a
file that is a rolling 24h window. This writes it out as data instead, so a
consumer can answer "what appeared today" with one fetch and no git.

Files are per-day and accumulate across the four runs of that UTC day: a domain
that shows up in the 05:17 run and is still gone at 23:17 stays recorded. A
domain that is added and then removed within the same day nets out of both
lists, because reporting it as both would be noise, not history.

The 350 KiB ceiling is deliberate: GitHub stops indexing a file for code search
above it, and being greppable from outside is most of the point of the mirror.
"""

import json
import os
import sys
from datetime import datetime, timezone

# GitHub's code-search indexer skips files above this. Staying under it is why
# the diff is per-day rather than one growing file.
MAX_BYTES = 350 * 1024


def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return {ln.strip() for ln in fh if ln.strip()}
    except FileNotFoundError:
        return set()


def main():
    if len(sys.argv) != 4:
        print("usage: build_changes.py <old_feed> <new_feed> <changes_dir>", file=sys.stderr)
        return 2
    old_path, new_path, changes_dir = sys.argv[1:4]

    old, new = _load(old_path), _load(new_path)
    added, removed = new - old, old - new
    if not added and not removed:
        print("No feed changes; nothing written.")
        return 0

    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    out_dir = os.path.join(changes_dir, now.strftime("%Y-%m"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{day}.json")

    prev = {}
    if os.path.exists(out_path):
        try:
            with open(out_path, encoding="utf-8") as fh:
                prev = json.load(fh)
        except (json.JSONDecodeError, OSError):
            # A corrupt day file must not wedge the mirror: start the day over
            # rather than failing the run. The git history still has the truth.
            prev = {}

    merged_added = set(prev.get("added", [])) | added
    merged_removed = set(prev.get("removed", [])) | removed
    # Netting: a domain that came and went inside the same day is not history,
    # it is churn. Dropping it from both lists keeps the file honest.
    both = merged_added & merged_removed
    merged_added -= both
    merged_removed -= both

    payload = {
        "date": day,
        "updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "https://phishunt.io/feed.txt",
        "license": "CC0-1.0",
        "counts": {"added": len(merged_added), "removed": len(merged_removed)},
        "added": sorted(merged_added),
        "removed": sorted(merged_removed),
    }
    body = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"

    if len(body.encode("utf-8")) > MAX_BYTES:
        # Truncate the larger list rather than the file: a day that busts the
        # ceiling is a day something went very wrong upstream, and the counts
        # plus a marker are more useful than a file GitHub will not index.
        key = "added" if len(merged_added) >= len(merged_removed) else "removed"
        payload["truncated"] = key
        keep = len(payload[key]) // 2
        payload[key] = payload[key][:keep]
        body = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"{out_path}: +{len(merged_added)} -{len(merged_removed)} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
