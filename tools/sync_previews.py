"""Copy finished preview pages from the public Supabase `previews` bucket (written by Drafted) into p/<slug>/.

    python3 tools/sync_previews.py

New slugs are added; a slug whose index.html changed is replaced. Hand-built pages that are not in the bucket (pocahontas, mcmullen) are never touched.
Prints the slugs it changed, one per line. The anon key is public by design; the bucket allows read only."""
import sys
from pathlib import Path

import requests

BASE = "https://mmaqwemqbxwngqxtnsug.supabase.co/storage/v1"
ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tYXF3ZW1xYnh3bmdxeHRuc3VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3NDY1MjgsImV4cCI6MjA5ODMyMjUyOH0.UrC1-5gGNODzu1PHU1QEqZAfzYhDbpQDlK3ruaIUDj0"
H = {"apikey": ANON, "Authorization": f"Bearer {ANON}"}
ROOT = Path(__file__).resolve().parent.parent


def ls(prefix):
    r = requests.post(f"{BASE}/object/list/previews", json={"prefix": prefix, "limit": 1000}, headers=H, timeout=60)
    r.raise_for_status()
    return r.json()


def get(key):
    r = requests.get(f"{BASE}/object/public/previews/{key}", timeout=60)
    r.raise_for_status()
    return r.content


def main():
    changed = []
    for ent in ls(""):
        if ent.get("id"):          # a file at the top level, not a slug folder
            continue
        slug = ent["name"]
        page = get(f"{slug}/index.html")
        dest = ROOT / "p" / slug
        if (dest / "index.html").exists() and (dest / "index.html").read_bytes() == page:
            continue
        (dest / "img").mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_bytes(page)
        for f in ls(f"{slug}/img"):
            if f.get("id"):
                (dest / "img" / f["name"]).write_bytes(get(f"{slug}/img/{f['name']}"))
        changed.append(slug)
    print("\n".join(changed))


if __name__ == "__main__":
    sys.exit(main())
