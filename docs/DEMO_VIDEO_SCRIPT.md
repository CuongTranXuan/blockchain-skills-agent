# Demo video (≈90 seconds) — record & upload

Use **QuickTime (macOS)**, **OBS**, or **Loom**. Upload as **YouTube Unlisted** or **Loom share link**, then set `DEMO_VIDEO_URL` and run the media update snippet in `SUBMISSION.md`.

## Suggested structure

| Time | Show | Say (short) |
|------|------|-------------|
| 0:00–0:15 | This static page or README | “Blockchain Skills Agent — portable markdown skills plus a real autonomous loop on Base for Synthesis.” |
| 0:15–0:35 | Repo tree: `skills/`, `agent/`, `agent.json` | “Skills teach validation and adaptation; the Python runtime runs discover through log with deterministic guardrails.” |
| 0:35–0:55 | Terminal: `pytest tests/ -q` then `python -m agent.main --scenario blocked-path --dry-run` | “Tests cover config and scenarios; blocked-path shows validation stopping a bad plan.” |
| 0:55–1:15 | **BaseScan** mainnet tx (link on this page) + `agent_log.json` excerpt | “Here is real mainnet execution via Uniswap Trading API and structured receipts.” |
| 1:15–1:30 | `CONVERSATION_LOG.md` or Synthesis project | “Human–agent collaboration and submission artifacts are documented for judges.” |

## Tips

- **720p** is enough; **clear tab title / folder name** in screen recording.
- Do **not** scroll through `.env` or any file that could show secrets.
- If you re-record after changing code, bump commit and mention the date in the video title.
