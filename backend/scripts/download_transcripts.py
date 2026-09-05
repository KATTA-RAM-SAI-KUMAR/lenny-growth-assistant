#!/usr/bin/env python3
"""
Transcript Downloader for The Lenny Growth Assistant
Fetches episode transcripts from the public Lenny's Podcast archive on GitHub.
"""

import os
import sys
import httpx
from pathlib import Path

GITHUB_API_URL = "https://api.github.com/repos/ChatPRD/lennys-podcast-transcripts/contents/episodes"
RAW_BASE_URL = "https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/main/episodes"
TARGET_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"

NOTABLE_EPISODES = [
    "brian-chesky",
    "shreyas-doshi",
    "elena-verna",
    "sean-ellis",
    "rahul-vohra",
    "gustaf-alstromer",
    "julie-zhuo",
    "geoffrey-moore",
]

def download_episode(slug: str):
    url = f"{RAW_BASE_URL}/{slug}/transcript.md"
    target_path = TARGET_DIR / f"{slug}.md"
    print(f"Fetching {slug} from {url}...")
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                target_path.write_text(resp.text, encoding="utf-8")
                print(f"  [OK] Saved to {target_path}")
            else:
                print(f"  [WARN] Episode {slug} returned status {resp.status_code}")
    except Exception as e:
        print(f"  [ERROR] Failed downloading {slug}: {e}")

def main():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target directory: {TARGET_DIR}")
    print(f"Downloading notable episodes...")
    for slug in NOTABLE_EPISODES:
        download_episode(slug)
    print("\nDownload process completed.")

if __name__ == "__main__":
    main()
