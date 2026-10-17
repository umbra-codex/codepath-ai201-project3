"""Flatten saved Reddit listing JSON files into one deduped CSV for reading/labeling."""
import csv, json, sys
from pathlib import Path

raw_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
rows, seen = [], set()
dropped = {"dup": 0, "removed": 0, "no_text": 0, "stickied": 0}
for f in sorted(raw_dir.glob("*.json")):
    for child in json.loads(f.read_text())["data"]["children"]:
        d = child["data"]
        if d["id"] in seen:
            dropped["dup"] += 1; continue
        seen.add(d["id"])
        body = (d.get("selftext") or "").strip()
        if body in ("[removed]", "[deleted]") or d.get("removed_by_category"):
            dropped["removed"] += 1; continue
        if d.get("stickied"):
            dropped["stickied"] += 1; continue
        title = d["title"].strip()
        text = f"{title}\n\n{body}" if body else title
        if not body and d.get("is_video") or (not body and d.get("post_hint") == "image"):
            # keep title-only image/meme posts; they are real WSB content
            pass
        rows.append({"id": d["id"], "flair": d.get("link_flair_text") or "",
                     "score": d["score"], "source": f.stem, "has_body": bool(body),
                     "url": "https://www.reddit.com" + d["permalink"],
                     "link_url": "" if d.get("is_self") else d.get("url_overridden_by_dest", ""),
                     "text": text})
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
md = ["# WSB reading sheet\n"]
for i, r in enumerate(sorted(rows, key=lambda r: -r["score"]), 1):
    md.append(f"## {i}. [{r['flair'] or 'no flair'}] score {r['score']}  ([thread]({r['url']}))")
    if r["link_url"]:
        md.append(f"Attached: {r['link_url']}")
    md.append("\n" + r["text"].replace("\n", "\n> ").join(["> ", ""]) + "\n")
(out.parent / "reading.md").write_text("\n".join(md))
print(f"{len(rows)} posts -> {out}  dropped={dropped}")
from collections import Counter
print("with body:", sum(r["has_body"] for r in rows), "title-only:", sum(not r["has_body"] for r in rows))
print("flairs:", Counter(r["flair"] or "(none)" for r in rows).most_common())
