# Synthesis — official skill URLs & API (reference)

Use this file to find **current** hackathon instructions from organizers. Always prefer these sources over stale copies.

## Official skill documents (hosted by organizers)

| Topic | URL | Notes |
|--------|-----|--------|
| **Registration** | `https://synthesis.md/skill.md` | `POST /register` flow, participant + API key |
| **Project submission** | `https://synthesis.devfolio.co/submission/skill.md` | Draft → publish, `conversationLog`, tracks, self-custody |
| **Wallet / ERC-8004 custody** | `https://synthesis.devfolio.co/wallet-setup/skill.md` | Self-custody transfer steps |
| **Wallet (alternate path in docs)** | `https://synthesis.md/wallet-setup/skill.md` | Same topic; use if one host is down |
| **Moltbook (optional)** | `https://www.moltbook.com/skill.md` | Submission checklist encourages `moltbookPostURL` |

## API base (submission & teams)

- **Base URL:** `https://synthesis.devfolio.co`
- **Auth (writes):** `Authorization: Bearer sk-synth-...` (key from registration; store in `.env` as `HACKATHON_API_KEY`, never commit)

Common calls:

| Action | Method | Path |
|--------|--------|------|
| Browse tracks | `GET` | `/catalog?page=1&limit=20` |
| Create draft project | `POST` | `/projects` |
| Update project (incl. `conversationLog`) | `POST` | `/projects/:projectUUID` |
| Publish | `POST` | `/projects/:projectUUID/publish` |
| Public read | `GET` | `/projects/:projectUUID` |
| Team details | `GET` | `/teams/:teamUUID` (auth) |

## Competition rules that affect your repo

From the [submission skill](https://synthesis.devfolio.co/submission/skill.md):

1. **`conversationLog` is required** on create and is **explicitly judged** — document brainstorms, pivots, and how the human and agent worked together.
2. **`submissionMetadata`** must be honest; judges cross-check against the conversation log and the repo.
3. **Self-custody** for all team members is required **before publish**.
4. **Track limits:** at least one track; checklist mentions **max 10 tracks plus Synthesis Open Track** — verify exact wording in the live skill if you change tracks.
5. **Open source:** `repoURL` must be a **public** GitHub repo by deadline.

## Local mirrors in this repo

- Hackathon context: `docs/reference/synthesis-hackathon-README.md`
- Tools / bounty mapping: `docs/ai/requirements/synthesis-tools-exploration.md`
- Human–agent narrative for judges: `CONVERSATION_LOG.md` (keep in sync with Devfolio `conversationLog` if you update the submission)
