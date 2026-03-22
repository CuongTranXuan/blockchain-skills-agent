#!/usr/bin/env python3
"""Push deployedURL, coverImageURL, pictures, and optional videoURL to Synthesis."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from dotenv import dotenv_values


DEFAULT_DEPLOYED = "https://cuongtranxuan.github.io/blockchain-skills-agent/"
RAW_BASE = "https://raw.githubusercontent.com/CuongTranXuan/blockchain-skills-agent/master/assets"
PROJECT_UUID = "98c345755ffc4b48b7e3b43ec7a017fd"

# Order: cover + architecture + scenario showcases (Synthesis `pictures` is comma-separated URLs).
PICTURE_FILENAMES = (
    "submission-cover.png",
    "submission-architecture.png",
    "scenario-happy-path.png",
    "scenario-blocked-path.png",
    "scenario-failure-path.png",
)


def _pictures_field() -> str:
    return ",".join(f"{RAW_BASE}/{name}" for name in PICTURE_FILENAMES)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--video-url",
        default=os.environ.get("DEMO_VIDEO_URL", "").strip(),
        help="YouTube / Loom URL (or set DEMO_VIDEO_URL)",
    )
    p.add_argument(
        "--no-video",
        action="store_true",
        help="Omit videoURL (images + deployed URL only)",
    )
    p.add_argument(
        "--deployed-url",
        default=DEFAULT_DEPLOYED,
        help="GitHub Pages URL for docs/",
    )
    args = p.parse_args()

    env = dotenv_values(".env")
    key = (env.get("HACKATHON_API_KEY") or "").strip()
    if not key:
        print("Missing HACKATHON_API_KEY in .env", file=sys.stderr)
        return 1

    cover = f"{RAW_BASE}/submission-cover.png"
    payload: dict = {
        "deployedURL": args.deployed_url.rstrip("/") + "/",
        "coverImageURL": cover,
        "pictures": _pictures_field(),
    }
    if not args.no_video:
        if not args.video_url:
            print(
                "No --video-url / DEMO_VIDEO_URL. Use --no-video to push images + deployed URL only.",
                file=sys.stderr,
            )
            return 1
        payload["videoURL"] = args.video_url

    req = urllib.request.Request(
        f"https://synthesis.devfolio.co/projects/{PROJECT_UUID}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            print(resp.status, body[:1200])
    except urllib.error.HTTPError as e:
        print(e.code, e.read().decode()[:2000], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
