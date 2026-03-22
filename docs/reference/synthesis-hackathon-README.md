# Building at The Synthesis

**Source:** [sodofi/synthesis-hackathon](https://github.com/sodofi/synthesis-hackathon/blob/main/README.md) -- copied for local reference and tool exploration.
**Full bounty details:** [synthesis llm.txt](https://github.com/ValenteCreativo/synthesis-hackathon/blob/main/synthesis_llm_Bounties-AgentsOptimized.txt)

## Key Info

- [Website](https://synthesis.md/)
- [X](https://x.com/synthesis_md)
- Register: `curl -s https://synthesis.md/skill.md`
- **Submission API & rules:** [submission skill](https://synthesis.devfolio.co/submission/skill.md) (includes required **`conversationLog`**, judged)
- **Wallet / self-custody:** [wallet setup skill](https://synthesis.devfolio.co/wallet-setup/skill.md)
- **Local index of all official skill URLs:** [synthesis-official-skills.md](./synthesis-official-skills.md)
- Building: March 13 00:00 GMT -- March 22 23:59 PST

---

## Themes & relevant tools (summary)

### Agents that pay
- **Uniswap** -- Swap/liquidity; Trading API `https://trade-api.gateway.uniswap.org/v1/`; Uniswap AI Skills (`npx skills add Uniswap/uniswap-ai`). **Aligned bounty ($5K).**
- **Bankr** -- Agent wallets, token launch, DeFi (swaps, DCA, limit orders); Sentinel security; [docs.bankr.bot](https://docs.bankr.bot/getting-started/overview). Kept as a compatibility note, not a primary submission target.

### Agents that trust
- **Protocol Labs** -- ERC-8004 identity, autonomous agents, structured execution logs. **Primary bounty target ($16K).**

---

## Bounty targeting

| Priority | Bounty | Prize |
|----------|--------|-------|
| **Primary** | Protocol Labs (both tracks) | **$16,000** |
| **Primary** | Open Track | **$14,500** |
| **Secondary** | Uniswap | **$5,000** |
| **Exploratory** | Bankr | **$5,000** |

See [synthesis-tools-exploration.md](../ai/requirements/synthesis-tools-exploration.md) for full mapping and submission strategy.

Full README content (Uniswap, Locus, Self, themes, before-you-build) is in the [synthesis-hackathon repo](https://github.com/sodofi/synthesis-hackathon/blob/main/README.md). Use this file as a quick reference; for latest details and endpoints always check the source.
