# Blockchain Skills for Agents

> Portable blockchain skills for any LLM agent, proven by a Base execution agent with ERC-8004 identity, structured receipts, and deterministic guardrails.

**Synthesis Hackathon 2026** | **Primary:** Protocol Labs + Open Track | **Secondary:** Uniswap | Exploratory: Bankr

## Submission Thesis

Most AI agents can talk about blockchain but cannot be trusted to operate onchain. They hallucinate token addresses, misuse decimals, ignore slippage, skip post-trade verification, and leave no trustworthy audit trail.

This project fixes that with two layers:

1. **Portable markdown skills** in `skills/` that teach any agent how to reason about balances, swaps, validation, debugging, and escalation.
2. **A working Python runtime** in `agent/` that proves those skills with a real autonomous loop on Base:

```text
discover -> plan -> validate -> execute -> verify -> log
```

The repo is optimized first for **Protocol Labs** and **Open Track**:
- trust anchored by **ERC-8004**
- structured evidence in **`agent.json`** and **`agent_log.json`**
- real tool usage via **Uniswap Trading API** and **Base RPC**
- deterministic safety checks before any execution

## Submission Scope

Current status: the repo now has a real **mainnet** proof run and a refreshed `agent_log.json`. Remaining work is submission packaging, not execution proof.

### What counts for submission

- **Mainnet evidence only** is included in the final submission package.
- The final showcased execution wallet is the mainnet wallet aligned with the submission story.
- The current `agent_log.json` contains the mainnet proof session used for submission.

### What testnet is for

- Testnet is used for development, debugging, and scenario rehearsal.
- Testnet wallets can be disposable and are **not** part of the final submission narrative.
- Scenario runs such as `blocked-path` and `failure-path` are used to demonstrate safety behavior during development and demos.

## Why This Is Valuable

- **Protocol Labs:** the project is a real autonomous system with identity, receipts, safety, and a clear operator model.
- **Open Track:** the core innovation is not “a trading bot,” but a reusable portability layer that can improve many agent frameworks.
- **Uniswap:** the execution path is grounded in real quote/build/swap behavior instead of mocks or screenshots.

## Mainnet Proof

- Wallet used for proof: `0xbE0888EDA826A963662aCe011775dd3F00C0463e`
- Network: Base mainnet
- Action: `0.005 ETH -> USDC`
- Transaction: [`0x50611f458c7533c461d0991e2e6315714c5991d119031783a60b3be80833a8db`](https://basescan.org/tx/0x50611f458c7533c461d0991e2e6315714c5991d119031783a60b3be80833a8db)
- Output amount: `11013555` raw USDC units
- Gas used: `136871`

## What Judges Can Inspect

| Artifact | Why it matters |
|----------|----------------|
| `skills/SKILL-INDEX.md` | Shows the portable skill system and entry points |
| `skills/skill-validate.md` | Shows deterministic safety and verification reasoning |
| `skills/skill-adapt.md` | Shows provider and chain adaptation patterns |
| `skills/skill-debug.md` | Shows failure handling and human escalation logic |
| `agent/main.py` | Shows the full Protocol Labs loop |
| `agent/execute.py` | Shows real Uniswap execution integration |
| `agent.json` | Shows ERC-8004 identity, capabilities, tools, and guardrails |
| `agent_log.json` | Shows structured execution receipts and evidence |
| `tests/` | Shows implementation rigor and reproducibility |

## Bounty Fit

### Protocol Labs: Let the Agent Cook

- Full autonomous loop: discover -> plan -> validate -> execute -> verify -> submit
- Real tool/API use
- Deterministic safety checks
- Structured verifiability via `agent_log.json`
- ERC-8004 identity and explicit agent manifest via `agent.json`

### Protocol Labs: Agents With Receipts

- ERC-8004 identity already integrated
- Agent/operator model is explicit in `agent.json`
- Submission evidence is onchain and mainnet-first
- `agent_log.json` is designed as the receipt surface for judges

### Open Track

- The strongest differentiator is the **portable skill layer**
- The repo combines agent design, execution safety, identity, and receipts into one coherent system
- The same skill artifacts can be reused in other agent runtimes, not just this Python demo

### Uniswap

- Real Uniswap Developer Platform integration
- Real swap flow support on Base
- Transparent documentation of quote/build/execute/verify behavior

### Bankr

- Kept as a secondary compatibility note in skills and architecture
- Not part of the primary submission story for this version

## Requirement Matrix

| Bounty requirement | Where it is shown |
|--------------------|-------------------|
| Autonomous loop | `agent/main.py`, `README.md`, `docs/ai/design/feature-blockchain-skill-for-agent.md` |
| ERC-8004 identity | `agent.json`, `.env`, `agent_log.json` |
| Agent manifest | `agent.json` |
| Execution receipts | `agent_log.json` |
| Real tool usage | `agent/execute.py`, final mainnet `agent_log.json` |
| Safety guardrails | `skills/skill-validate.md`, `agent/validate.py`, `agent.json` |
| Real-world usefulness | `README.md`, `skills/`, real mainnet run |
| Open Track coherence | `README.md`, `docs/ai/requirements/feature-blockchain-skill-for-agent.md`, `docs/ai/design/feature-blockchain-skill-for-agent.md` |

## How It Works

### Skill Layer

| Skill | Purpose |
|-------|---------|
| `SKILL-INDEX.md` | Registry, triggers, quick-start |
| `skill-validate.md` | Pre-tx validation and post-tx verification |
| `skill-adapt.md` | Provider and chain adaptation patterns |
| `skill-debug.md` | Failure diagnosis and human escalation |

These skills are plain markdown and intentionally framework-agnostic.

### Runtime Layer

The Python agent:
- discovers the wallet portfolio from Base RPC
- plans an action using an LLM with skill context
- validates the plan in deterministic code
- executes through Uniswap or dry-run mode
- verifies outcomes against the original intent
- logs every phase in `agent_log.json`

### Demo Scenarios

- `default`: normal autonomous behavior
- `happy-path`: conservative success path
- `blocked-path`: intentionally unsafe plan that validation blocks
- `failure-path`: valid plan followed by simulated provider failure

These scenarios strengthen the Protocol Labs story by showing not just success, but also guardrails and failure handling.

## Architecture

```text
Human operator
    |
    v
Portable skills (.md) -> LLM reasoning -> Python runtime
                                         |-> Base RPC
                                         |-> Uniswap Trading API
                                         `-> agent_log.json / notifications
```

## Quick Start

```bash
# use the existing project venv
.venv/bin/python -m pytest tests/ -v

# dry-run demo scenarios
.venv/bin/python -m agent.main --scenario happy-path --dry-run
.venv/bin/python -m agent.main --scenario blocked-path --dry-run
.venv/bin/python -m agent.main --scenario failure-path --dry-run

# live execution (NETWORK in .env decides testnet vs mainnet)
.venv/bin/python -m agent.main
```

## Project Structure

```text
synthesis/
├── skills/
├── agent/
├── tests/
├── agent.json
├── agent_log.json
├── README.md
└── docs/
```

## Current Validation

- `.venv/bin/python -m pytest tests/ -v` -> `56 passed`
- Scenario dry-runs verified for `happy-path`, `blocked-path`, and `failure-path`

## Final Submission Checklist

- Confirm the submission wallet/operator story matches `agent.json`
- Keep the repo public and the README unchanged after the final proof run
- Include the mainnet tx hash and explorer link prominently in submission text
- Submit against **Protocol Labs** and **Open Track** first; include Uniswap as secondary

## License

MIT
