from __future__ import annotations

from agent.llm import LLMClient
from agent.scenarios import scenario_planning_note
from agent.types import Plan, Portfolio

WETH = "0x4200000000000000000000000000000000000006"  # same on all Base chains


def _portfolio_prompt(portfolio: Portfolio) -> str:
    lines = [
        f"Chain: {portfolio.chain} (chainId={portfolio.chain_id})",
        f"Wallet: {portfolio.address}",
        "Balances:",
    ]
    for t in portfolio.tokens:
        if t.balance > 0 or t.symbol == "ETH":
            lines.append(f"  {t.symbol}: {t.balance:.8f}")
    return "\n".join(lines)


def _system_prompt(skills: str, chain_id: int, scenario: str = "default") -> str:
    testnet_note = ""
    if chain_id != 8453:
        testnet_note = """
IMPORTANT - TESTNET MODE:
This is a testnet chain. Uniswap has very limited liquidity for most pairs.
The ONLY reliable swap on testnet is ETH -> WETH (wrapping). Always suggest this action
if the wallet has any ETH balance, so the agent can demonstrate a real on-chain transaction.
Use action="swap", token_in="ETH", token_out="WETH", token_out_address="0x4200000000000000000000000000000000000006".
Keep amount_in small (e.g. 0.001 ETH) to conserve testnet gas.
"""
    scenario_note = scenario_planning_note(scenario)

    return f"""You are a DeFi agent using portable blockchain skills to manage a wallet.

{skills}
{testnet_note}
{scenario_note}
You MUST reply with a single JSON object (no markdown fences):
{{
  "action": "swap" | "no-action",
  "token_in": "ETH" | "WETH" | "USDC" | ...,
  "token_out": "ETH" | "WETH" | "USDC" | ...,
  "token_in_address": "<checksum address or empty string for native ETH>",
  "token_out_address": "<checksum address>",
  "amount_in": <float>,
  "slippage": <float between 0.001 and 0.05>,
  "reason": "<1-2 sentence justification>",
  "summary": "<short human-readable label>"
}}

Rules:
- If ETH balance is below 0.0002, set action to "no-action".
- For ETH (native), use empty string "" for token_in_address.
- slippage is the decimal tolerance (e.g. 0.005 = 0.5%).
- Keep amount_in ≤ 50% of available ETH to leave gas.
"""


def plan_with_llm(llm: LLMClient, skills: str, portfolio: Portfolio, scenario: str = "default") -> Plan:
    """Ask the LLM to propose an action given the current portfolio."""
    system = _system_prompt(skills, portfolio.chain_id, scenario=scenario)
    user_msg = (
        f"Current portfolio:\n{_portfolio_prompt(portfolio)}\n\n"
        "What action should I take? Reply with JSON only."
    )

    result = llm.reason(system_prompt=system, user_message=user_msg)

    action = result.get("action", "no-action")
    token_in = result.get("token_in", "ETH")
    token_out = result.get("token_out", "WETH")
    amount_in = float(result.get("amount_in", 0.0))
    slippage = float(result.get("slippage", 0.005))
    reason = result.get("reason", "LLM provided no reason.")
    summary = result.get("summary", f"{action}: {token_in}->{token_out} {amount_in}")

    token_in_address = result.get("token_in_address", "")
    token_out_address = result.get("token_out_address", WETH)

    return Plan(
        action=action,
        token_in=token_in,
        token_out=token_out,
        token_in_address=token_in_address,
        token_out_address=token_out_address,
        amount_in=amount_in,
        amount_in_raw=None,
        slippage=slippage,
        chain_id=portfolio.chain_id,
        reason=reason,
        summary=summary,
    )
