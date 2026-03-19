"""Agent configuration.

Single-toggle network switching via NETWORK env var (or --network CLI flag):

    NETWORK=testnet   → Base Sepolia (84532), uses TESTNET_* vars
    NETWORK=mainnet   → Base Mainnet  (8453),  uses MAINNET_* vars

Every network-specific setting is read as  {NETWORK_PREFIX}_{KEY}
with sensible defaults so unset vars don't cause crashes.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv

# ─── Static per-chain metadata ────────────────────────────────────────────────

CHAIN_CONFIGS: dict[int, dict] = {
    8453: {
        "name": "base",
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org",
        "uniswap_chain": "base",      # kept for documentation; API now uses chain_id
        "tokens": {
            "WETH": "0x4200000000000000000000000000000000000006",
            "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",
            "DAI":  "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
        },
    },
    84532: {
        "name": "base_sepolia",
        "rpc": "https://sepolia.base.org",
        "explorer": "https://sepolia.basescan.org",
        "uniswap_chain": "base_sepolia",
        "tokens": {
            "WETH": "0x4200000000000000000000000000000000000006",
            "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        },
    },
}

NETWORK_CHAIN_IDS = {"mainnet": 8453, "testnet": 84532}


# ─── Config dataclass ─────────────────────────────────────────────────────────

@dataclass
class Config:
    # Identity
    erc8004_address: str
    network: str          # "mainnet" | "testnet"

    # Chain
    chain_id: int
    rpc_url: str

    # Wallet
    operator_key: str     # private key hex (with or without 0x prefix)

    # APIs
    uniswap_api_key: str
    bankr_api_key: str

    # LLM
    llm_api_key: str
    llm_model: str
    llm_base_url: str | None

    # Runtime
    provider: str          # "uniswap" | "bankr" | "dry-run"
    max_tx_value_usd: float

    # ── Derived properties ────────────────────────────────────────────────────

    @property
    def chain_name(self) -> str:
        return CHAIN_CONFIGS.get(self.chain_id, {}).get("name", "unknown")

    @property
    def explorer(self) -> str:
        return CHAIN_CONFIGS.get(self.chain_id, {}).get("explorer", "https://basescan.org")

    @property
    def tokens(self) -> dict[str, str]:
        return CHAIN_CONFIGS.get(self.chain_id, {}).get("tokens", {})

    @property
    def is_testnet(self) -> bool:
        return self.chain_id != 8453

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_env(
        cls,
        network: str | None = None,
        dry_run: bool = False,
        provider: str | None = None,
    ) -> "Config":
        load_dotenv()

        if not os.getenv("LLM_API_KEY"):
            print("ERROR: Missing required env var: LLM_API_KEY")
            sys.exit(1)

        # ── 1. Resolve network (mainnet | testnet) ───────────────────────────
        resolved_network = (
            network
            or os.getenv("NETWORK", "testnet")
        ).lower()

        if resolved_network not in NETWORK_CHAIN_IDS:
            print(f"ERROR: NETWORK must be 'mainnet' or 'testnet', got '{resolved_network}'")
            sys.exit(1)

        prefix = resolved_network.upper()   # "MAINNET" or "TESTNET"
        chain_id = NETWORK_CHAIN_IDS[resolved_network]
        chain_cfg = CHAIN_CONFIGS[chain_id]

        # ── 2. Network-prefixed vars with fallbacks ──────────────────────────
        #  Lookup order:  MAINNET_FOO  →  BASE_FOO (legacy)  →  built-in default
        rpc_url = (
            os.getenv(f"{prefix}_RPC_URL")
            or os.getenv("BASE_RPC_URL")
            or chain_cfg["rpc"]
        )
        operator_key = (
            os.getenv(f"{prefix}_WALLET_KEY")
            or os.getenv("OPERATOR_WALLET_KEY", "")
        )
        max_tx = float(
            os.getenv(f"{prefix}_MAX_TX_VALUE_USD")
            or os.getenv("MAX_TX_VALUE_USD", "100")
        )
        raw_provider = (
            provider
            or os.getenv(f"{prefix}_PROVIDER")
            or os.getenv("PROVIDER", "uniswap")
        )

        # ── 3. Resolve provider ──────────────────────────────────────────────
        resolved_provider = raw_provider
        if dry_run:
            resolved_provider = "dry-run"
        elif resolved_network == "testnet" and resolved_provider == "bankr":
            print("[config] Bankr is mainnet-only — falling back to 'uniswap' on testnet.")
            resolved_provider = "uniswap"

        return cls(
            erc8004_address=os.getenv("ERC8004_ADDRESS", ""),
            network=resolved_network,
            chain_id=chain_id,
            rpc_url=rpc_url,
            operator_key=operator_key,
            uniswap_api_key=os.getenv("UNISWAP_API_KEY", ""),
            bankr_api_key=os.getenv("BANKR_API_KEY", ""),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_base_url=os.getenv("LLM_BASE_URL") or None,
            provider=resolved_provider,
            max_tx_value_usd=max_tx,
        )

    def summary(self) -> str:
        net = "TESTNET" if self.is_testnet else "MAINNET"
        return (
            f"{net} | {self.chain_name} (chain {self.chain_id}) | "
            f"provider={self.provider} | max_tx=${self.max_tx_value_usd}"
        )
