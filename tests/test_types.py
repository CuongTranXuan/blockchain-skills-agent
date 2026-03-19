from agent.types import TokenBalance, Portfolio, Plan, ValidationResult, TxResult, Verification


def test_token_balance():
    t = TokenBalance(symbol="USDC", address="0xabc", balance_raw=1_000_000, decimals=6)
    assert t.balance == 1.0
    d = t.to_dict()
    assert d["symbol"] == "USDC"
    assert d["balance"] == "1.0"


def test_token_balance_eth():
    t = TokenBalance(symbol="ETH", address="", balance_raw=10**18, decimals=18)
    assert t.balance == 1.0


def test_portfolio_summary():
    p = Portfolio(
        chain="base", chain_id=8453, address="0xTEST",
        tokens=[
            TokenBalance("ETH", "", 10**16, 18),
            TokenBalance("USDC", "0xabc", 5_000_000, 6),
        ],
    )
    assert "ETH: 0.01" in p.summary
    assert "USDC: 5.0" in p.summary
    d = p.to_dict()
    assert len(d["tokens"]) == 2


def test_plan_to_dict():
    plan = Plan(action="swap", token_in="ETH", token_out="USDC", amount_in=0.001)
    d = plan.to_dict()
    assert d["action"] == "swap"
    assert d["amount_in"] == 0.001


def test_validation_result():
    v = ValidationResult(valid=True, checks=[{"name": "test", "passed": True, "detail": "ok"}])
    assert v.to_dict()["valid"] is True


def test_tx_result_minimal():
    tx = TxResult()
    d = tx.to_dict()
    assert d["status"] == "pending"
    assert "block_number" not in d


def test_tx_result_full():
    tx = TxResult(hash="0x1", status="success", block_number=100, gas_used=21000)
    d = tx.to_dict()
    assert d["block_number"] == 100


def test_verification():
    v = Verification(confirmed=True, matches_intent=True, details="ok")
    assert v.to_dict()["confirmed"] is True
