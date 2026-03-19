"""End-to-end test of the full autonomous loop with mocked externals."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.discover import discover
from agent.execute import execute_swap_dry_run
from agent.llm import LLMClient
from agent.logger import AgentLogger
from agent.plan import plan_with_llm
from agent.types import Plan, Portfolio, TokenBalance, TxResult
from agent.validate import validate_intent
from agent.verify import verify_outcome


def _mock_portfolio() -> Portfolio:
    return Portfolio(
        chain="base", chain_id=8453, address="0xTEST",
        tokens=[
            TokenBalance("ETH", "", 10**16, 18),
            TokenBalance("USDC", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 50_000_000, 6),
        ],
    )


def _mock_llm_swap_response() -> dict:
    return {
        "action": "swap",
        "token_in": "ETH",
        "token_in_address": "",
        "token_out": "USDC",
        "token_out_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "amount_in": 0.001,
        "slippage": 0.005,
        "chain_id": 8453,
        "estimated_value_usd": 3.0,
        "reason": "Small demo swap of ETH to USDC to demonstrate agent capabilities",
        "summary": "Swap 0.001 ETH -> USDC on Base via Uniswap",
    }


def _mock_llm_no_action_response() -> dict:
    return {
        "action": "no-action",
        "reason": "Wallet has very little ETH, need to preserve for gas",
        "summary": "No action — insufficient funds for a safe demo swap",
    }


class TestEndToEndSwapLoop:
    """Full loop: discover -> plan -> validate -> execute -> verify -> log."""

    def test_successful_swap_loop(self):
        portfolio = _mock_portfolio()
        llm = MagicMock(spec=LLMClient)
        llm.reason.return_value = _mock_llm_swap_response()

        skills = "test skills context"
        plan = plan_with_llm(llm, skills, portfolio)
        assert plan.action == "swap"
        assert plan.token_in == "ETH"
        assert plan.token_out == "USDC"

        validation = validate_intent(plan, portfolio, 100.0)
        assert validation.valid is True

        tx_result = execute_swap_dry_run(plan)
        assert tx_result.status == "success"

        w3_mock = MagicMock()
        verification = verify_outcome(tx_result, plan, w3_mock)
        assert verification.confirmed is True
        assert verification.matches_intent is True

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            log_path = f.name
        log = AgentLogger("0xDEMO", output_path=log_path)
        log.entry("discover", "read-portfolio", "skill-adapt.md", {}, portfolio)
        log.entry("plan", plan.action, "skill-validate.md", {}, plan)
        log.entry("plan", "pre-tx-validation", "skill-validate.md", {}, validation)
        log.entry("execute", plan.action, "skill-adapt.md", {}, tx_result)
        log.entry("verify", "verify-outcome", "skill-validate.md", {}, verification)
        result = log.finalize()

        assert len(result["entries"]) == 5
        phases = [e["phase"] for e in result["entries"]]
        assert phases == ["discover", "plan", "plan", "execute", "verify"]

        saved = json.loads(Path(log_path).read_text())
        assert saved["erc8004"] == "0xDEMO"

    def test_no_action_loop(self):
        portfolio = _mock_portfolio()
        llm = MagicMock(spec=LLMClient)
        llm.reason.return_value = _mock_llm_no_action_response()

        plan = plan_with_llm(llm, "skills", portfolio)
        assert plan.action == "no-action"
        assert "insufficient" in plan.reason.lower() or "gas" in plan.reason.lower()

    def test_validation_blocks_bad_plan(self):
        portfolio = _mock_portfolio()
        llm = MagicMock(spec=LLMClient)
        resp = _mock_llm_swap_response()
        resp["amount_in"] = 100.0
        resp["estimated_value_usd"] = 300_000
        llm.reason.return_value = resp

        plan = plan_with_llm(llm, "skills", portfolio)
        validation = validate_intent(plan, portfolio, 100.0)
        assert validation.valid is False


class TestDiscoverIntegration:
    """Test discover with mocked web3."""

    def test_discover_returns_portfolio(self):
        w3 = MagicMock()
        w3.eth.get_balance.return_value = 10**16
        w3.eth.chain_id = 8453

        contract_mock = MagicMock()
        contract_mock.functions.balanceOf.return_value.call.return_value = 5_000_000
        contract_mock.functions.decimals.return_value.call.return_value = 6
        contract_mock.functions.symbol.return_value.call.return_value = "USDC"
        w3.eth.contract.return_value = contract_mock

        portfolio = discover(w3, "0x1234567890abcdef1234567890abcdef12345678")
        assert portfolio.chain == "base"
        assert portfolio.chain_id == 8453
        assert len(portfolio.tokens) >= 1
        assert portfolio.tokens[0].symbol == "ETH"


class TestExecuteVerify:

    def test_dry_run_produces_valid_result(self):
        plan = Plan(action="swap", token_in="ETH", token_out="USDC")
        tx = execute_swap_dry_run(plan)
        assert tx.status == "success"
        assert tx.hash.startswith("0x")
        assert tx.gas_used == 185_000

    def test_verify_dry_run(self):
        plan = Plan(action="swap", token_out_address="0xabc")
        tx = execute_swap_dry_run(plan)
        w3 = MagicMock()
        v = verify_outcome(tx, plan, w3)
        assert v.confirmed is True
        assert "Dry-run" in v.details

    def test_verify_failure(self):
        plan = Plan(action="swap")
        tx = TxResult(status="failure", error="Simulated failure")
        w3 = MagicMock()
        v = verify_outcome(tx, plan, w3)
        assert v.confirmed is False
        assert "failed" in v.details.lower()
