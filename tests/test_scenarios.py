from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agent.llm import LLMClient
from agent.plan import plan_with_llm
from agent.scenarios import (
    apply_plan_scenario,
    normalize_scenario,
    scenario_execution_result,
)
from agent.types import Plan, Portfolio, TokenBalance
from agent.validate import validate_intent


def _portfolio() -> Portfolio:
    return Portfolio(
        chain="base_sepolia",
        chain_id=84532,
        address="0xTEST",
        tokens=[TokenBalance("ETH", "", 10**16, 18)],
    )


def _llm_plan() -> dict:
    return {
        "action": "swap",
        "token_in": "ETH",
        "token_in_address": "",
        "token_out": "WETH",
        "token_out_address": "0x4200000000000000000000000000000000000006",
        "amount_in": 0.001,
        "slippage": 0.005,
        "reason": "Safe testnet wrap.",
        "summary": "Wrap 0.001 ETH to WETH",
    }


def test_normalize_scenario_defaults():
    assert normalize_scenario(None) == "default"
    assert normalize_scenario("HAPPY-PATH") == "happy-path"


def test_normalize_scenario_rejects_invalid():
    with pytest.raises(ValueError):
        normalize_scenario("wild")


def test_plan_with_happy_path_includes_scenario_note():
    llm = MagicMock(spec=LLMClient)
    llm.reason.return_value = _llm_plan()

    plan = plan_with_llm(llm, "skills", _portfolio(), scenario="happy-path")

    assert plan.action == "swap"
    system_prompt = llm.reason.call_args.kwargs["system_prompt"]
    assert "HAPPY PATH" in system_prompt


def test_blocked_path_modifies_plan_and_validation_blocks():
    portfolio = _portfolio()
    plan = Plan(
        action="swap",
        token_in="ETH",
        token_out="WETH",
        token_out_address="0x4200000000000000000000000000000000000006",
        amount_in=0.001,
        slippage=0.005,
        chain_id=84532,
        reason="base plan",
        summary="base plan",
    )

    plan = apply_plan_scenario(plan, portfolio, "blocked-path")
    validation = validate_intent(plan, portfolio, 5.0)

    assert plan.slippage == 0.08
    assert validation.valid is False
    assert any(check["name"] == "slippage-bounds" and not check["passed"] for check in validation.checks)


def test_failure_path_returns_forced_execution_error():
    plan = Plan(action="swap", summary="demo failure swap")
    tx_result = scenario_execution_result("failure-path", plan)

    assert tx_result is not None
    assert tx_result.status == "failure"
    assert "simulated" in tx_result.error.lower()


def test_non_failure_scenario_does_not_force_execution_result():
    plan = Plan(action="swap", summary="demo swap")
    assert scenario_execution_result("happy-path", plan) is None
