from __future__ import annotations

from agent.types import Plan, Portfolio, TxResult

DEFAULT_SCENARIO = "default"
SUPPORTED_SCENARIOS = {
    "default",
    "happy-path",
    "blocked-path",
    "failure-path",
}


def normalize_scenario(value: str | None) -> str:
    scenario = (value or DEFAULT_SCENARIO).strip().lower()
    if scenario not in SUPPORTED_SCENARIOS:
        supported = ", ".join(sorted(SUPPORTED_SCENARIOS))
        raise ValueError(f"Unsupported scenario '{value}'. Choose one of: {supported}")
    return scenario


def scenario_description(scenario: str) -> str:
    descriptions = {
        "default": "Normal autonomous behavior using live portfolio conditions.",
        "happy-path": "A safe, low-risk demo trade that should pass validation and execute cleanly.",
        "blocked-path": "An intentionally unsafe plan that deterministic validation should block.",
        "failure-path": "A valid plan followed by a simulated execution failure for debugging and recovery demos.",
    }
    return descriptions[scenario]


def scenario_planning_note(scenario: str) -> str:
    if scenario == "happy-path":
        return (
            "DEMO SCENARIO - HAPPY PATH:\n"
            "Prioritize a conservative, low-risk action that is likely to succeed and demonstrates the full loop.\n"
            "Prefer a small swap that leaves ample gas reserve.\n"
        )
    if scenario == "blocked-path":
        return (
            "DEMO SCENARIO - BLOCKED PATH:\n"
            "Propose an aggressive swap that would normally be tempting but should be rejected by safety checks.\n"
            "Use a large enough size or slippage to trigger validation failure.\n"
        )
    if scenario == "failure-path":
        return (
            "DEMO SCENARIO - FAILURE PATH:\n"
            "Propose a valid, conservative swap that can proceed to execution.\n"
            "The runtime will simulate an external execution failure to demonstrate debugging and audit logging.\n"
        )
    return ""


def apply_plan_scenario(plan: Plan, portfolio: Portfolio, scenario: str) -> Plan:
    if scenario == "happy-path":
        if not plan.summary:
            plan.summary = f"Demo happy path: {plan.token_in}->{plan.token_out}"
        plan.reason = f"{plan.reason} [scenario=happy-path]".strip()
        return plan

    if scenario == "blocked-path":
        eth_token = next((t for t in portfolio.tokens if t.symbol == "ETH"), None)
        blocked_amount = max((eth_token.balance if eth_token else 0.001) * 0.95, 0.001)
        plan.action = "swap"
        plan.token_in = "ETH"
        plan.token_in_address = ""
        plan.token_out = "WETH"
        plan.token_out_address = "0x4200000000000000000000000000000000000006"
        plan.amount_in = blocked_amount
        plan.amount_in_raw = None
        plan.slippage = 0.08
        plan.reason = "Scenario forces an intentionally risky trade so deterministic validation can block it."
        plan.summary = f"Blocked demo: attempt to swap {blocked_amount:.6f} ETH with 8.0% slippage"
        return plan

    if scenario == "failure-path":
        if plan.action == "no-action":
            eth_token = next((t for t in portfolio.tokens if t.symbol == "ETH"), None)
            available = eth_token.balance if eth_token else 0.0
            plan.action = "swap"
            plan.token_in = "ETH"
            plan.token_in_address = ""
            plan.token_out = "WETH"
            plan.token_out_address = "0x4200000000000000000000000000000000000006"
            plan.amount_in = min(max(available * 0.1, 0.001), 0.002)
            plan.slippage = 0.005
        plan.reason = "Scenario uses a valid plan and then simulates an execution-provider failure."
        plan.summary = f"Failure demo: {plan.token_in}->{plan.token_out} then simulate quote/provider failure"
        return plan

    return plan


def scenario_execution_result(scenario: str, plan: Plan) -> TxResult | None:
    if scenario != "failure-path":
        return None
    return TxResult(
        status="failure",
        error=(
            "Demo scenario simulated an execution failure: quote unavailable / provider rejected the build. "
            f"Action was {plan.summary}"
        ),
    )
