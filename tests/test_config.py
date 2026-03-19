import os
from unittest.mock import patch

import pytest

from agent.config import Config


# ── Helpers ───────────────────────────────────────────────────────────────────

def _base_env(**overrides):
    """Minimal valid env vars common to all tests."""
    base = {
        "LLM_API_KEY": "test-key",
        "LLM_MODEL": "gpt-4o-mini",
        "ERC8004_ADDRESS": "0xabc",
        "UNISWAP_API_KEY": "uni-key",
        "BANKR_API_KEY": "bnk-key",
        # testnet defaults
        "TESTNET_WALLET_KEY": "0xdeadbeef",
        "TESTNET_RPC_URL": "https://sepolia.base.org",
        "TESTNET_PROVIDER": "uniswap",
        "TESTNET_MAX_TX_VALUE_USD": "5",
        # mainnet defaults
        "MAINNET_WALLET_KEY": "0xdeadcafe",
        "MAINNET_RPC_URL": "https://mainnet.base.org",
        "MAINNET_PROVIDER": "uniswap",
        "MAINNET_MAX_TX_VALUE_USD": "20",
    }
    base.update(overrides)
    return base


# ── Network toggle tests ──────────────────────────────────────────────────────

def test_default_network_is_testnet():
    env = _base_env()
    env.pop("NETWORK", None)
    with patch.dict(os.environ, env, clear=True):
        cfg = Config.from_env()
    assert cfg.network == "testnet"
    assert cfg.chain_id == 84532
    assert cfg.is_testnet is True


def test_network_env_mainnet():
    with patch.dict(os.environ, _base_env(NETWORK="mainnet"), clear=True):
        cfg = Config.from_env()
    assert cfg.network == "mainnet"
    assert cfg.chain_id == 8453
    assert cfg.is_testnet is False


def test_network_env_testnet():
    with patch.dict(os.environ, _base_env(NETWORK="testnet"), clear=True):
        cfg = Config.from_env()
    assert cfg.network == "testnet"
    assert cfg.chain_id == 84532


def test_network_arg_overrides_env():
    """CLI --network arg takes priority over NETWORK env var."""
    with patch.dict(os.environ, _base_env(NETWORK="testnet"), clear=True):
        cfg = Config.from_env(network="mainnet")
    assert cfg.network == "mainnet"
    assert cfg.chain_id == 8453


# ── Per-network settings picked up correctly ─────────────────────────────────

def test_testnet_uses_testnet_vars():
    with patch.dict(os.environ, _base_env(NETWORK="testnet"), clear=True):
        cfg = Config.from_env()
    assert cfg.rpc_url == "https://sepolia.base.org"
    assert cfg.operator_key == "0xdeadbeef"
    assert cfg.max_tx_value_usd == 5.0


def test_mainnet_uses_mainnet_vars():
    with patch.dict(os.environ, _base_env(NETWORK="mainnet"), clear=True):
        cfg = Config.from_env()
    assert cfg.rpc_url == "https://mainnet.base.org"
    assert cfg.operator_key == "0xdeadcafe"
    assert cfg.max_tx_value_usd == 20.0


# ── Provider resolution ───────────────────────────────────────────────────────

def test_dry_run_overrides_provider():
    with patch.dict(os.environ, _base_env(NETWORK="mainnet"), clear=True):
        cfg = Config.from_env(dry_run=True)
    assert cfg.provider == "dry-run"


def test_bankr_allowed_on_mainnet():
    with patch.dict(os.environ, _base_env(NETWORK="mainnet", MAINNET_PROVIDER="bankr"), clear=True):
        cfg = Config.from_env()
    assert cfg.provider == "bankr"


def test_bankr_fallback_to_uniswap_on_testnet():
    with patch.dict(os.environ, _base_env(NETWORK="testnet", TESTNET_PROVIDER="bankr"), clear=True):
        cfg = Config.from_env()
    assert cfg.provider == "uniswap"


def test_provider_arg_overrides_env():
    """CLI --provider arg takes priority over {NETWORK}_PROVIDER."""
    with patch.dict(os.environ, _base_env(NETWORK="mainnet", MAINNET_PROVIDER="uniswap"), clear=True):
        cfg = Config.from_env(provider="bankr")
    assert cfg.provider == "bankr"


# ── Derived properties ────────────────────────────────────────────────────────

def test_chain_name_mainnet():
    with patch.dict(os.environ, _base_env(NETWORK="mainnet"), clear=True):
        cfg = Config.from_env()
    assert cfg.chain_name == "base"


def test_chain_name_testnet():
    with patch.dict(os.environ, _base_env(NETWORK="testnet"), clear=True):
        cfg = Config.from_env()
    assert cfg.chain_name == "base_sepolia"


def test_tokens_mainnet_includes_dai():
    with patch.dict(os.environ, _base_env(NETWORK="mainnet"), clear=True):
        cfg = Config.from_env()
    assert "DAI" in cfg.tokens


def test_tokens_testnet_excludes_dai():
    with patch.dict(os.environ, _base_env(NETWORK="testnet"), clear=True):
        cfg = Config.from_env()
    assert "DAI" not in cfg.tokens


def test_summary_contains_network_info():
    with patch.dict(os.environ, _base_env(NETWORK="testnet"), clear=True):
        cfg = Config.from_env()
    s = cfg.summary()
    assert "TESTNET" in s
    assert "84532" in s


# ── Error cases ───────────────────────────────────────────────────────────────

def test_missing_llm_key_exits():
    env = _base_env(NETWORK="testnet")
    env["LLM_API_KEY"] = ""
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(SystemExit):
            Config.from_env()


def test_invalid_network_exits():
    with patch.dict(os.environ, _base_env(NETWORK="staging"), clear=True):
        with pytest.raises(SystemExit):
            Config.from_env()
