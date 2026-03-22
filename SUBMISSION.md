# Submission Package

Current status: this repo is **submission-ready** and includes a successful **mainnet** `happy-path` proof run in `agent_log.json`. The project is **published** on Synthesis/Devfolio (see **Synthesis project** below).

This repo is being submitted with **Protocol Labs** and **Open Track** as the primary targets.

## Synthesis project (Devfolio API)

| Field | Value |
|--------|--------|
| **Project UUID** | `98c345755ffc4b48b7e3b43ec7a017fd` |
| **Public API** | `GET https://synthesis.devfolio.co/projects/98c345755ffc4b48b7e3b43ec7a017fd` |
| **Status** | `publish` when live |

## Official hackathon skills & competition updates

Canonical list of organizer URLs (registration, submission, wallet, Moltbook):  
**[`docs/reference/synthesis-official-skills.md`](docs/reference/synthesis-official-skills.md)**

The live **[submission skill](https://synthesis.devfolio.co/submission/skill.md)** states that **`conversationLog` is required** and is **judged** — it must reflect real human–agent collaboration (brainstorms, pivots, breakthroughs). Judges may cross-check it against `submissionMetadata` and the repo.

### Where the conversation log lives

1. **In the platform:** the `conversationLog` string on your Synthesis **project** (created/updated via API or UI).
2. **In this repo:** **`CONVERSATION_LOG.md`** — expanded narrative; **keep these aligned** if you edit one.

### How to submit or update `conversationLog` (API)

Requires `HACKATHON_API_KEY` in `.env` (never commit). Per [submission skill](https://synthesis.devfolio.co/submission/skill.md), updates use `POST /projects/:projectUUID` with at least one field; include the **full** `submissionMetadata` object when updating metadata (see skill).

```bash
# Example: refresh conversationLog from file (jq wraps as JSON string)
export HACKATHON_API_KEY="sk-synth-..."   # or: source from .env locally
PROJECT_UUID="98c345755ffc4b48b7e3b43ec7a017fd"
CONVERSATION="$(jq -Rs . < CONVERSATION_LOG.md)"

curl -sS -X POST "https://synthesis.devfolio.co/projects/${PROJECT_UUID}" \
  -H "Authorization: Bearer ${HACKATHON_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"conversationLog\": ${CONVERSATION}}"
```

If the API rejects a partial update, send the fields the skill allows for that endpoint, or use the Devfolio **web dashboard** for the same project and paste from `CONVERSATION_LOG.md`.

## Live demo, cover image, screenshots, video (Synthesis form / API)

### 1) Enable GitHub Pages (one-time)

Repo: **`CuongTranXuan/blockchain-skills-agent`** · source: **`master`** · folder **`/docs`**.

GitHub → **Settings** → **Pages** → **Build and deployment** → **Deploy from a branch** → Branch **`master`**, folder **`/docs`** → Save.

After propagation, the live URL is:

**`https://cuongtranxuan.github.io/blockchain-skills-agent/`**

(Use this as **`deployedURL`** on Synthesis.)

### 2) Cover + screenshots (hosted on `raw.githubusercontent.com`)

After your latest commit is on **`master`**, these links are stable:

| Field | URL |
|--------|-----|
| **coverImageURL** | `https://raw.githubusercontent.com/CuongTranXuan/blockchain-skills-agent/master/assets/submission-cover.png` |
| **pictures** (both images, comma-separated) | `https://raw.githubusercontent.com/CuongTranXuan/blockchain-skills-agent/master/assets/submission-cover.png,https://raw.githubusercontent.com/CuongTranXuan/blockchain-skills-agent/master/assets/submission-architecture.png` |

Source files in repo: `assets/submission-cover.png`, `assets/submission-architecture.png` (also copied under `docs/assets/` for the static site).

### 3) Demo video (**required** on your checklist)

We **cannot** host a compliant video only inside the repo (Synthesis expects a **video URL**). Record ~90s using **`docs/DEMO_VIDEO_SCRIPT.md`**, upload (**YouTube Unlisted** or **Loom**), then set **`videoURL`** to that link.

### 4) Push media fields to Synthesis (API)

From repo root (uses `HACKATHON_API_KEY` from `.env`):

```bash
# Images + live demo URL only (enable GitHub Pages first — see above)
.venv/bin/python scripts/push_submission_media.py --no-video

# After you upload a demo recording (see docs/DEMO_VIDEO_SCRIPT.md):
export DEMO_VIDEO_URL="https://www.youtube.com/watch?v=YOUR_ID"
.venv/bin/python scripts/push_submission_media.py --video-url "$DEMO_VIDEO_URL"
```

If you need to update **without** a video yet, use `--no-video` (some dashboards may still show “video required” until you run the second command).

## Submission Story

- `testnet` is development-only and is not part of the final judging evidence
- the final proof surface is a **mainnet** run on Base
- the final submission should point judges to:
  - `README.md`
  - `agent.json`
  - `agent_log.json`
  - `skills/`
  - `agent/`

## Mainnet Proof

- Wallet: `0xbE0888EDA826A963662aCe011775dd3F00C0463e`
- Action: `0.005 ETH -> USDC`
- Tx hash: [`0x50611f458c7533c461d0991e2e6315714c5991d119031783a60b3be80833a8db`](https://basescan.org/tx/0x50611f458c7533c461d0991e2e6315714c5991d119031783a60b3be80833a8db)
- Output amount: `11013555` raw USDC units
- Gas used: `136871`

## What To Show

### Protocol Labs

- ERC-8004 identity in `agent.json`
- autonomous loop in `agent/main.py`
- structured receipts in `agent_log.json`
- deterministic guardrails in `agent/validate.py` and `skills/skill-validate.md`

### Open Track

- portable markdown skills as the core innovation
- coherent system design across identity, execution, validation, and receipts
- reusable agent literacy layer that is not tied to this single runtime

### Uniswap

- real Developer Platform integration in `agent/execute.py`
- real mainnet tx hash in `agent_log.json`

## Submission checklist vs [official skill](https://synthesis.devfolio.co/submission/skill.md)

Checked against the live **Submission Checklist** (pre-publish + post-publish).

| Checklist item | Status | Notes |
|----------------|--------|--------|
| All team members **self-custody** | **Done** | Required to publish; project reached `publish`. |
| `name` set | **Done** | Published project has a clear name. |
| `description` | **Done** | Elevator pitch on Synthesis + README. |
| `problemStatement` | **Done** | Specific onchain-agent trust problem. |
| `repoURL` public GitHub | **Done** | Public repo linked on submission. |
| `trackUUIDs` (≥1) | **Done** | Protocol Labs ×2, Open Track, Uniswap. |
| `conversationLog` | **Improve** | Short version was sent at create time; **`CONVERSATION_LOG.md`** now has the full anonymized thread — **sync to Synthesis** via `POST /projects/:uuid` or dashboard (see above). |
| `submissionMetadata.agentFramework` / `agentHarness` / `model` | **Done** | `other` + `agentFrameworkOther`, `cursor`, `gpt-4o-mini`. |
| `submissionMetadata.skills` / `tools` | **Review** | Keep **honest**: only list skill IDs the harness actually loaded. Update on Synthesis if you change the list. |
| `helpfulResources` / `helpfulSkills` | **Done** | Present on published metadata. |
| `intention` | **Done** | `continuing` + notes. |
| **`moltbookPostURL`** | **Missing** | Checklist expects a Moltbook post URL — [Moltbook skill](https://www.moltbook.com/skill.md). Add via project **update** when you have a post. |
| **`deployedURL`** | **Set after Pages** | Use GitHub Pages from `/docs` → `https://cuongtranxuan.github.io/blockchain-skills-agent/` |
| **`videoURL`** | **You upload** | Record using `docs/DEMO_VIDEO_SCRIPT.md`; set `DEMO_VIDEO_URL` and run the media snippet above. |
| **`coverImageURL` / `pictures`** | **In repo** | `assets/submission-cover.png` + `assets/submission-architecture.png` (raw.githubusercontent URLs in section above). |
| After publish: `status: publish` + listing | **Done** | Verified via public `GET /projects/...`. |
| `commitCount` / commit timestamps | **May lag** | Re-push commits then **update** project (same `repoURL`) so metadata refreshes. |
| **Tweet** tagging `@synthesis_md` | **Optional / recommended** | For visibility per skill doc. |

## Final Pre-Submission Steps

- confirm `agent.json` matches the intended submission operator story
- keep the repo public with the current README and submission artifacts
- sync **`CONVERSATION_LOG.md`** → Synthesis `conversationLog` after edits
- add **`moltbookPostURL`** and/or **`videoURL`** when available

## Commands

```bash
# regression tests
.venv/bin/python -m pytest tests/ -v

# dev/demo rehearsal
.venv/bin/python -m agent.main --scenario happy-path --dry-run
.venv/bin/python -m agent.main --scenario blocked-path --dry-run
.venv/bin/python -m agent.main --scenario failure-path --dry-run

# final proof run
.venv/bin/python -m agent.main --network mainnet --scenario happy-path
```
