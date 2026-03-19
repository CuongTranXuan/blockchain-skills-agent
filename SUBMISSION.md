# Submission Package

Current status: this repo is **submission-ready** and now includes a successful **mainnet** `happy-path` proof run in `agent_log.json`.

This repo is being submitted with **Protocol Labs** and **Open Track** as the primary targets.

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

## Final Pre-Submission Steps

- confirm `agent.json` matches the intended submission operator story
- keep the repo public with the current README and submission artifacts

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
