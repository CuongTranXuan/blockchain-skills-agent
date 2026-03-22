# Blockchain Skills for Agents — Index

> Portable, harness-agnostic skill files that teach any AI agent how to safely operate on blockchain. Load these into your agent's context (system prompt, RAG, file read) and follow the instructions.

## Skills

| Skill | File | When to load |
|-------|------|-------------|
| **Validate** | `skill-validate.md` | Before AND after any on-chain transaction. Always load this skill. |
| **Adapt** | `skill-adapt.md` | When interacting with a specific provider (Uniswap, Bankr) or chain (Base). Load when you need to build or submit a transaction. |
| **Debug** | `skill-debug.md` | When a transaction fails, an API returns an error, or something unexpected happens. Load when troubleshooting. |

## Quick start

1. Load all skills into your agent's context.
2. Agent reads portfolio on-chain (skill-adapt: Base RPC section).
3. Agent proposes an operation and validates intent (skill-validate: pre-tx checklist).
4. Agent executes the transaction (skill-adapt: provider-specific section).
5. Agent verifies the outcome (skill-validate: post-tx verification).
6. If anything fails, agent diagnoses and notifies human (skill-debug).

## Supported providers

- **Uniswap Trading API** — swap quotes and execution on Base (and 25+ other chains).
- **Bankr** — agent wallets, DeFi operations (swaps, DCA, limit orders), Sentinel security layer, LLM Gateway.
- **Base RPC** — direct chain queries via any web3 library (balances, token metadata, receipts).

## Supported chain

- **Base** (chain ID 8453) — Ethereum L2. All examples use Base. The same patterns apply to other EVM chains by changing the RPC URL and chain ID.

## Key behaviors these skills enable

1. **Validate every transaction** before signing — catch wrong decimals, insufficient balance, stale quotes, wrong chain.
2. **Verify outcomes** after execution — confirm the on-chain result matches the intended operation.
3. **Adapt to any provider** — same reasoning pattern whether using Uniswap, Bankr, or raw RPC calls.
4. **Debug failures** automatically — diagnose why a transaction failed and produce an actionable summary for the human.
5. **Notify the human** when it matters — large transactions, failures, fraud signals, approval requests.

## Synthesis hackathon context

These skills are built for the [Synthesis](https://synthesis.md/) hackathon. Official organizer docs (registration, submission, wallet, API notes): see **[`docs/reference/synthesis-official-skills.md`](../docs/reference/synthesis-official-skills.md)**.

The demo agent uses ERC-8004 identity (on Base Mainnet), references a checked-in `agent.json`, writes `agent_log.json` at runtime, and targets:

- **Protocol Labs** — "Let the Agent Cook" + "Agents With Receipts"
- **Open Track** — cross-sponsor agent system
- **Bankr** — skills complement Sentinel
- **Uniswap** — real swaps with validation

Theme alignment: **Agents that pay** (scoped spending, auditable history, conditional execution) and **Agents that trust** (ERC-8004, structured logs).
