from agent.types import Plan, Portfolio, TokenBalance
from agent.validate import validate_intent


def _portfolio(eth_raw: int = 10**16) -> Portfolio:
    return Portfolio(
        chain="base", chain_id=8453, address="0xTEST",
        tokens=[
            TokenBalance("ETH", "", eth_raw, 18),
            TokenBalance("USDC", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 50_000_000, 6),
        ],
    )


def _plan(**overrides) -> Plan:
    defaults = dict(
        action="swap", token_in="ETH", token_in_address="",
        token_out="USDC", token_out_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        amount_in=0.001, slippage=0.005, chain_id=8453, estimated_value_usd=3.0,
        reason="test", summary="test swap",
    )
    defaults.update(overrides)
    return Plan(**defaults)


def test_valid_plan():
    r = validate_intent(_plan(), _portfolio(), 100.0)
    assert r.valid is True
    assert all(c["passed"] for c in r.checks)


def test_insufficient_balance():
    r = validate_intent(_plan(amount_in=100.0), _portfolio(), 100.0)
    assert r.valid is False
    assert any("balance" in c["name"] and not c["passed"] for c in r.checks)


def test_exceeds_safety_limit():
    r = validate_intent(_plan(estimated_value_usd=200.0), _portfolio(), 100.0)
    assert r.valid is False
    assert any("safety" in c["name"] and not c["passed"] for c in r.checks)


def test_wrong_chain():
    r = validate_intent(_plan(chain_id=1), _portfolio(), 100.0)
    assert r.valid is False
    assert any("chain" in c["name"] and not c["passed"] for c in r.checks)


def test_slippage_too_high():
    r = validate_intent(_plan(slippage=0.10), _portfolio(), 100.0)
    assert r.valid is False
    assert any("slippage" in c["name"] and not c["passed"] for c in r.checks)


def test_zero_amount():
    r = validate_intent(_plan(amount_in=0.0), _portfolio(), 100.0)
    assert r.valid is False
    assert any("amount" in c["name"] and not c["passed"] for c in r.checks)


def test_token_not_in_portfolio():
    plan = _plan(token_in="WBTC")
    r = validate_intent(plan, _portfolio(), 100.0)
    assert r.valid is False
    assert any("balance" in c["name"] and not c["passed"] for c in r.checks)
