#!/usr/bin/env python3
"""TikTok-Video-Protokoll: was wurde gepostet, wie lief es.

Nur Standardbibliothek. Daten liegen in tiktok/videos.json (wird committet,
damit neue Sitzungen den Verlauf kennen).

  python3 tiktok/log.py add --title "..." --hook "..." [--niche X] [--model X]
        [--prompt "..."] [--script "..."] [--caption "..."] [--hashtags "#a #b"]
        [--sound "..."] [--length 12] [--url URL] [--posted 2026-11-18]
  python3 tiktok/log.py stats <id> --views 300 [--avg-watch 4.1] [--completion 12]
        [--likes N] [--comments N] [--shares N] [--saves N] [--follows N] [--fyp 85]
  python3 tiktok/log.py note <id> "Text"
  python3 tiktok/log.py list
  python3 tiktok/log.py show <id>
  python3 tiktok/log.py report
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).resolve().parent / "videos.json"
STAT_FIELDS = ["views", "avg_watch", "completion", "likes", "comments",
               "shares", "saves", "follows", "fyp"]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load():
    if not DB.exists():
        return {"videos": []}
    return json.loads(DB.read_text(encoding="utf-8"))


def save(data):
    DB.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")


def find(data, vid):
    for v in data["videos"]:
        if v["id"] == vid:
            return v
    sys.exit(f"Unbekannte ID: {vid}")


def latest(v):
    return v["stats"][-1] if v.get("stats") else {}


def retention(v):
    s = latest(v)
    if s.get("avg_watch") and v.get("length_s"):
        return round(100 * s["avg_watch"] / v["length_s"])
    return None


def cmd_add(a, data):
    vid = f"v{len(data['videos']) + 1:03d}"
    row = {"id": vid, "logged": now()}
    for k in ["title", "hook", "niche", "model", "prompt", "script",
              "caption", "hashtags", "sound", "url", "posted"]:
        if getattr(a, k):
            row[k] = getattr(a, k)
    if a.length:
        row["length_s"] = a.length
    row["stats"], row["notes"] = [], []
    data["videos"].append(row)
    save(data)
    print(f"Gespeichert: {vid} — {a.title}")


def cmd_stats(a, data):
    v = find(data, a.id)
    snap = {"at": now()}
    for k in STAT_FIELDS:
        val = getattr(a, k)
        if val is not None:
            snap[k] = val
    v.setdefault("stats", []).append(snap)
    save(data)
    r = retention(v)
    print(f"{a.id}: {snap.get('views', '?')} Views"
          + (f", Retention {r}%" if r is not None else ""))


def cmd_note(a, data):
    find(data, a.id).setdefault("notes", []).append(f"{now()[:10]}: {a.text}")
    save(data)
    print("Notiz gespeichert.")


def cmd_list(a, data):
    for v in data["videos"]:
        s, r = latest(v), retention(v)
        print(f"{v['id']}  {v.get('posted', v['logged'][:10])}  "
              f"{str(s.get('views', '-')):>7} Views  "
              f"{(str(r) + '%') if r is not None else '-':>5}  "
              f"{v.get('title', '')}  | Hook: {v.get('hook', '')}")


def cmd_show(a, data):
    print(json.dumps(find(data, a.id), ensure_ascii=False, indent=2))


def cmd_report(a, data):
    vids = [v for v in data["videos"] if latest(v).get("views") is not None]
    if not vids:
        print("Noch keine Videos mit Zahlen. Erst `stats` eintragen.")
        return
    vids.sort(key=lambda v: latest(v)["views"], reverse=True)
    views = [latest(v)["views"] for v in vids]
    print(f"{len(data['videos'])} Videos, {len(vids)} mit Zahlen. "
          f"Ø {round(sum(views) / len(views))} Views, Median "
          f"{sorted(views)[len(views) // 2]}.")
    print("\nTop 5:")
    for v in vids[:5]:
        print(f"  {v['id']} {latest(v)['views']:>7}  Retention "
              f"{retention(v) if retention(v) is not None else '-'}%  "
              f"Hook: {v.get('hook', '')}")
    print("\nSchwächste 5:")
    for v in vids[-5:]:
        print(f"  {v['id']} {latest(v)['views']:>7}  Retention "
              f"{retention(v) if retention(v) is not None else '-'}%  "
              f"Hook: {v.get('hook', '')}")


def main():
    p = argparse.ArgumentParser(description="TikTok-Video-Protokoll")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add")
    s.add_argument("--title", required=True)
    s.add_argument("--hook", required=True)
    for k in ["niche", "model", "prompt", "script", "caption", "hashtags",
              "sound", "url", "posted"]:
        s.add_argument(f"--{k}")
    s.add_argument("--length", type=float, help="Videolänge in Sekunden")

    s = sub.add_parser("stats")
    s.add_argument("id")
    for k in ["views", "likes", "comments", "shares", "saves", "follows"]:
        s.add_argument(f"--{k}", type=int)
    s.add_argument("--avg-watch", dest="avg_watch", type=float,
                   help="Ø Wiedergabedauer in Sekunden")
    s.add_argument("--completion", type=float, help="Ganz angesehen in %%")
    s.add_argument("--fyp", type=float, help="Anteil 'Für dich' in %%")

    s = sub.add_parser("note")
    s.add_argument("id")
    s.add_argument("text")

    sub.add_parser("list")
    s = sub.add_parser("show")
    s.add_argument("id")
    sub.add_parser("report")

    a = p.parse_args()
    data = load()
    {"add": cmd_add, "stats": cmd_stats, "note": cmd_note, "list": cmd_list,
     "show": cmd_show, "report": cmd_report}[a.cmd](a, data)


if __name__ == "__main__":
    main()
