from __future__ import annotations

from agent.types import Plan, Portfolio, ValidationResult


def validate_intent(plan: Plan, portfolio: Portfolio, max_tx_value_usd: float) -> ValidationResult:
    """Deterministic pre-tx validation implementing skill-validate checklist.

    No LLM involved — this is pure code enforcing the skill rules.
    """
    checks: list[dict] = []

    # 1. Balance sufficient
    if plan.action == "swap":
        token = next((t for t in portfolio.tokens if t.symbol == plan.token_in), None)
        if token:
            ok = token.balance >= plan.amount_in
            checks.append({
                "name": "balance-sufficient",
                "passed": ok,
                "detail": f"{token.balance} {plan.token_in} {'>=':} {plan.amount_in}",
            })
        else:
            checks.append({
                "name": "balance-sufficient",
                "passed": False,
                "detail": f"Token {plan.token_in} not found in portfolio",
            })

    # 2. Within safety limit
    ok = plan.estimated_value_usd <= max_tx_value_usd
    checks.append({
        "name": "within-safety-limit",
        "passed": ok,
        "detail": f"${plan.estimated_value_usd:.2f} vs ${max_tx_value_usd:.2f} limit",
    })

    # 3. Chain ID correct
    ok = plan.chain_id == portfolio.chain_id
    checks.append({
        "name": "chain-id-correct",
        "passed": ok,
        "detail": f"plan chain {plan.chain_id} vs portfolio chain {portfolio.chain_id}",
    })

    # 4. Slippage within bounds
    ok = plan.slippage <= 0.05
    checks.append({
        "name": "slippage-bounds",
        "passed": ok,
        "detail": f"{plan.slippage * 100:.1f}% (max 5%)",
    })

    # 5. Amount positive
    ok = plan.amount_in > 0
    checks.append({
        "name": "amount-positive",
        "passed": ok,
        "detail": f"amount_in = {plan.amount_in}",
    })

    all_ok = all(c["passed"] for c in checks)
    reason = None if all_ok else "; ".join(c["detail"] for c in checks if not c["passed"])
    return ValidationResult(valid=all_ok, checks=checks, reason=reason)
