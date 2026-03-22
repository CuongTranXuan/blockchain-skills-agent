# Demo video (≈90 seconds) — record & upload

**Silent base video (dub later):** run `./scripts/build_demo_silent_video.sh` → `demo/output/demo-silent-for-dub-1080p.mp4` (slideshow of repo showcase images + silent audio track). Narrate in any editor, then export and upload.

**Or record live:** **QuickTime (macOS)**, **OBS**, or **Loom**. Upload as **YouTube Unlisted** or **Loom share link**, then set `DEMO_VIDEO_URL` and run the media update in **`SUBMISSION.md`** / **`demo/README.md`**.

## Suggested structure

| Time | Show | Say (short) |
|------|------|-------------|
| 0:00–0:12 | This static page (hero) | “Portable skills plus a real Base agent loop for Synthesis.” |
| 0:12–0:28 | Scroll **Demo scenarios** (happy / blocked / failure) on the same page | “Mainnet proof path plus guardrails and failure handling.” |
| 0:28–0:48 | Repo: `skills/`, `agent/`, `agent.json` | “Skills encode the playbook; the runtime enforces validation before execution.” |
| 0:48–1:08 | Terminal: `pytest tests/ -q` and `python -m agent.main --scenario blocked-path --dry-run` | “Tests and blocked-path show deterministic safety.” |
| 1:08–1:25 | **BaseScan** mainnet tx + `agent_log.json` snippet | “Real swap via Uniswap Trading API and structured receipts.” |
| 1:25–1:35 | `CONVERSATION_LOG.md` or submission | “Human–agent build process is documented for judges.” |

## Tips

- **720p** is enough; **clear tab title / folder name** in screen recording.
- Do **not** scroll through `.env` or any file that could show secrets.
- If you re-record after changing code, bump commit and mention the date in the video title.

