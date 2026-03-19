"""Blockchain Skills Agent — autonomous loop on Base.

Usage:
    python -m agent.main                          # uses NETWORK from .env (default: testnet)
    python -m agent.main --network mainnet        # override to mainnet
    python -m agent.main --network testnet        # override to testnet
    python -m agent.main --dry-run                # simulate, no real transactions
    python -m agent.main --scenario happy-path    # guided demo scenario
    python -m agent.main --provider bankr         # force Bankr (mainnet only)
    python -m agent.main --provider uniswap       # force Uniswap Trading API
    python -m agent.main --network mainnet --dry-run   # mainnet dry-run (safe preview)
"""
from __future__ import annotations

import asyncio
import sys

from web3 import Web3

from agent.config import Config
from agent.discover import discover
from agent.execute import execute_swap_bankr, execute_swap_dry_run, execute_swap_uniswap
from agent.llm import LLMClient
from agent.logger import AgentLogger
from agent.notify import notify
from agent.plan import plan_with_llm
from agent.scenarios import (
    normalize_scenario,
    scenario_description,
    scenario_execution_result,
    apply_plan_scenario,
)
from agent.skills_loader import load_skills
from agent.validate import validate_intent
from agent.verify import verify_outcome


def _parse_args() -> dict:
    """Minimal CLI arg parser (no external dependencies)."""
    args: dict = {"dry_run": False, "network": None, "provider": None, "scenario": "default"}
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--dry-run":
            args["dry_run"] = True
        elif tok in ("--network", "-n") and i + 1 < len(argv):
            args["network"] = argv[i + 1]
            i += 1
        elif tok in ("--provider", "-p") and i + 1 < len(argv):
            args["provider"] = argv[i + 1]
            i += 1
        elif tok in ("--scenario", "-s") and i + 1 < len(argv):
            args["scenario"] = argv[i + 1]
            i += 1
        i += 1
    try:
        args["scenario"] = normalize_scenario(args["scenario"])
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    return args


async def autonomous_loop(config: Config, scenario: str = "default") -> dict:
    """Protocol Labs loop: discover → plan → validate → execute → verify → log."""
    w3 = Web3(Web3.HTTPProvider(config.rpc_url))
    if not w3.is_connected():
        print(f"ERROR: Cannot connect to RPC {config.rpc_url}")
        sys.exit(1)

    # Derive wallet address from private key (or bail if missing for live providers)
    if config.operator_key:
        key = config.operator_key if config.operator_key.startswith("0x") else "0x" + config.operator_key
        account = w3.eth.account.from_key(key)
        wallet_address = account.address
        private_key = key
    elif config.provider == "dry-run":
        wallet_address = "0x0000000000000000000000000000000000000000"
        private_key = ""
    else:
        print(
            f"ERROR: {config.network.upper()}_WALLET_KEY is not set in .env. "
            "Set it, or run with --dry-run to simulate."
        )
        sys.exit(1)

    llm = LLMClient(api_key=config.llm_api_key, model=config.llm_model, base_url=config.llm_base_url)
    skills = load_skills()
    log = AgentLogger(config.erc8004_address)

    print(f"Agent started | {config.summary()}")
    print(f"Wallet        | {wallet_address}")
    print(f"Scenario      | {scenario} — {scenario_description(scenario)}")
    print(f"Skills loaded | {len(skills)} chars")

    # ── 1. DISCOVER ──────────────────────────────────────────────────────────
    print("\n[1/5] DISCOVER — reading portfolio...")
    portfolio = discover(w3, wallet_address)
    log.entry("discover", "read-portfolio", "skill-adapt.md",
              {"chain": config.chain_name, "address": wallet_address, "scenario": scenario}, portfolio)
    print(portfolio.summary)

    eth_token = next((t for t in portfolio.tokens if t.symbol == "ETH"), None)
    if eth_token and eth_token.balance < 0.0001 and config.provider != "dry-run":
        msg = (
            f"ETH balance too low ({eth_token.balance:.8f} ETH). "
            f"Fund {wallet_address} and retry."
        )
        print(f"\n{msg}")
        notify(msg)
        log.entry("submit", "insufficient-funds", "skill-debug.md", {}, {"reason": msg})
        return log.finalize()

    # ── 2. PLAN ──────────────────────────────────────────────────────────────
    print("\n[2/5] PLAN — LLM analyzing portfolio with skills...")
    plan = plan_with_llm(llm, skills, portfolio, scenario=scenario)
    plan = apply_plan_scenario(plan, portfolio, scenario)
    log.entry("plan", plan.action, "skill-validate.md",
              {"portfolio_summary": portfolio.summary, "scenario": scenario}, plan)
    print(f"Action:  {plan.action}")
    print(f"Summary: {plan.summary}")
    print(f"Reason:  {plan.reason}")

    if plan.action == "no-action":
        summary = f"No action taken: {plan.reason}"
        notify(summary)
        log.entry("submit", "no-action", "skill-debug.md", {}, {"summary": summary})
        return log.finalize()

    # ── 3. VALIDATE ──────────────────────────────────────────────────────────
    print("\n[3/5] VALIDATE — pre-tx checks (skill-validate)...")
    validation = validate_intent(plan, portfolio, config.max_tx_value_usd)
    log.entry("plan", "pre-tx-validation", "skill-validate.md",
              {"plan_summary": plan.summary, "scenario": scenario}, validation)

    for check in validation.checks:
        label = "PASS" if check["passed"] else "FAIL"
        print(f"  [{label}] {check['name']}: {check['detail']}")

    if not validation.valid:
        msg = f"Validation BLOCKED: {validation.reason}"
        print(f"\n{msg}")
        notify(f"Status: BLOCKED\nAction: {plan.summary}\nReason: {validation.reason}")
        log.entry("submit", "validation-blocked", "skill-debug.md", {}, {"reason": validation.reason})
        return log.finalize()

    print("  All checks passed — proceeding.")

    # ── 4. EXECUTE ───────────────────────────────────────────────────────────
    print(f"\n[4/5] EXECUTE — {config.provider.upper()} | {plan.action}...")
    forced_result = scenario_execution_result(scenario, plan)
    if forced_result is not None:
        tx_result = forced_result
    elif config.provider == "dry-run":
        tx_result = execute_swap_dry_run(plan)
    elif config.provider == "bankr":
        tx_result = await execute_swap_bankr(plan, config.bankr_api_key)
    else:
        tx_result = await execute_swap_uniswap(
            plan, w3, wallet_address, private_key,
            uniswap_api_key=config.uniswap_api_key,
            chain_id=config.chain_id,
        )

    log.entry("execute", plan.action, "skill-adapt.md",
              {"plan_summary": plan.summary, "provider": config.provider, "scenario": scenario}, tx_result)
    print(f"Tx hash: {tx_result.hash}")
    print(f"Status:  {tx_result.status}")
    if tx_result.error:
        print(f"Error:   {tx_result.error}")

    if tx_result.status == "failure":
        notify(f"Status: FAILURE\nAction: {plan.summary}\nError: {tx_result.error}")
        log.entry("submit", "execution-failed", "skill-debug.md", {}, {"error": tx_result.error})
        return log.finalize()

    # ── 5. VERIFY ────────────────────────────────────────────────────────────
    print("\n[5/5] VERIFY — post-tx verification (skill-validate)...")
    verification = verify_outcome(tx_result, plan, w3)
    log.entry("verify", "verify-outcome", "skill-validate.md",
              {"tx_hash": tx_result.hash, "scenario": scenario}, verification)
    print(f"Confirmed:      {verification.confirmed}")
    print(f"Matches intent: {verification.matches_intent}")
    print(f"Details:        {verification.details}")

    # ── NOTIFY ───────────────────────────────────────────────────────────────
    is_dry = config.provider == "dry-run"
    explorer_url = f"{config.explorer}/tx/{tx_result.hash}" if not is_dry else "(dry-run)"
    summary_msg = (
        f"Status:      {'SUCCESS' if verification.confirmed else 'NEEDS REVIEW'}\n"
        f"Network:     {config.summary()}\n"
        f"Action:      {plan.summary}\n"
        f"Provider:    {config.provider}\n"
        f"Tx hash:     {tx_result.hash}\n"
        f"Amount out:  {tx_result.amount_out}\n"
        f"Gas used:    {tx_result.gas_used}\n"
        f"Explorer:    {explorer_url}"
    )
    notify(summary_msg)
    log.entry("submit", "notify-human", "skill-debug.md", {}, {"summary": summary_msg})

    return log.finalize()


def main() -> None:
    args = _parse_args()
    config = Config.from_env(
        network=args["network"],
        dry_run=args["dry_run"],
        provider=args["provider"],
    )
    asyncio.run(autonomous_loop(config, scenario=args["scenario"]))


if __name__ == "__main__":
    main()
