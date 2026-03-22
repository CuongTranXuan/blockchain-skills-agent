# Demo video (silent, for dubbing)

We **cannot** capture your real screen from the AI environment. Instead, generate a **silent 1080p slideshow** from the PNGs in `assets/` — easy to **narrate / dub** in CapCut, iMovie, DaVinci, Premiere, etc.

## Build (local)

```bash
chmod +x scripts/build_demo_silent_video.sh
./scripts/build_demo_silent_video.sh
```

Output (gitignored): **`demo/output/demo-silent-for-dub-1080p.mp4`**

- **H.264**, 1920×1080, ~**72s** (adjust durations in the script).
- Includes a **silent stereo AAC** track so editors that require audio don’t complain (`ADD_SILENT_AUDIO=0` to omit).

Requires **ffmpeg** (`brew install ffmpeg`).

## After you dub

Upload to YouTube (unlisted) or Loom, then:

```bash
export DEMO_VIDEO_URL='https://...'
.venv/bin/python scripts/push_submission_media.py --video-url "$DEMO_VIDEO_URL"
```

See **`docs/DEMO_VIDEO_SCRIPT.md`** for what to say over each section.
