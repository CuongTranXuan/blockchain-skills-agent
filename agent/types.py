from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenBalance:
    symbol: str
    address: str  # "" for native ETH
    balance_raw: int
    decimals: int

    @property
    def balance(self) -> float:
        return self.balance_raw / (10 ** self.decimals)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "address": self.address,
            "balance": str(self.balance),
            "balance_raw": str(self.balance_raw),
            "decimals": self.decimals,
        }


@dataclass
class Portfolio:
    chain: str
    chain_id: int
    address: str
    tokens: list[TokenBalance] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [f"Portfolio on {self.chain} (chain {self.chain_id}) for {self.address}:"]
        for t in self.tokens:
            lines.append(f"  {t.symbol}: {t.balance} (decimals={t.decimals})")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "chain": self.chain,
            "chain_id": self.chain_id,
            "address": self.address,
            "tokens": [t.to_dict() for t in self.tokens],
            "summary": self.summary,
        }


@dataclass
class Plan:
    action: str  # "swap", "transfer", "no-action"
    token_in: str = ""
    token_in_address: str = ""
    token_out: str = ""
    token_out_address: str = ""
    amount_in: float = 0.0
    amount_in_raw: str | None = None
    slippage: float = 0.005
    chain_id: int = 8453
    estimated_value_usd: float = 0.0
    reason: str = ""
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "token_in": self.token_in,
            "token_in_address": self.token_in_address,
            "token_out": self.token_out,
            "token_out_address": self.token_out_address,
            "amount_in": self.amount_in,
            "amount_in_raw": self.amount_in_raw,
            "slippage": self.slippage,
            "chain_id": self.chain_id,
            "estimated_value_usd": self.estimated_value_usd,
            "reason": self.reason,
            "summary": self.summary,
        }


@dataclass
class ValidationResult:
    valid: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    reason: str | None = None

    def to_dict(self) -> dict:
        return {"valid": self.valid, "checks": self.checks, "reason": self.reason}


@dataclass
class TxResult:
    hash: str = ""
    status: str = "pending"  # "success", "failure", "pending"
    block_number: int | None = None
    gas_used: int | None = None
    amount_out: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        d: dict[str, Any] = {"hash": self.hash, "status": self.status}
        if self.block_number is not None:
            d["block_number"] = self.block_number
        if self.gas_used is not None:
            d["gas_used"] = self.gas_used
        if self.amount_out:
            d["amount_out"] = self.amount_out
        if self.error:
            d["error"] = self.error
        return d


@dataclass
class Verification:
    confirmed: bool = False
    matches_intent: bool = False
    actual_amount_out: str = ""
    block_number: int | None = None
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "confirmed": self.confirmed,
            "matches_intent": self.matches_intent,
            "actual_amount_out": self.actual_amount_out,
            "block_number": self.block_number,
            "details": self.details,
        }
