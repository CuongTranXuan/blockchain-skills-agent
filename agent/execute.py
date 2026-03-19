from __future__ import annotations

import asyncio
import json

import httpx
from web3 import Web3
from eth_account.messages import encode_typed_data

from agent.types import Plan, TxResult

UNISWAP_API = "https://trade-api.gateway.uniswap.org/v1"
BANKR_API = "https://api.bankr.bot"


def _amount_to_raw(amount: float, decimals: int) -> str:
    return str(int(amount * (10 ** decimals)))


def _extract_amount_out(quote_obj: dict) -> str:
    """Pull amountOut from either old-style (amountOut) or new-style (output.amount) quote."""
    if "output" in quote_obj and isinstance(quote_obj["output"], dict):
        return str(quote_obj["output"].get("amount", ""))
    return str(quote_obj.get("amountOut", ""))


def _normalize_tx_hash(value: bytes | str) -> str:
    """Return transaction hashes in canonical 0x-prefixed lowercase hex."""
    if isinstance(value, bytes):
        return "0x" + value.hex()
    hash_str = str(value)
    return hash_str if hash_str.startswith("0x") else "0x" + hash_str


async def execute_swap_uniswap(
    plan: Plan,
    w3: Web3,
    wallet_address: str,
    private_key: str,
    uniswap_api_key: str,
    uniswap_chain: str = "base",  # kept for backwards-compat but not sent to API anymore
    chain_id: int = 8453,
) -> TxResult:
    """Execute a swap via Uniswap Trading API (v1, current spec).

    Uses tokenInChainId/tokenOutChainId (numeric) and x-permit2-disabled
    for a simple direct-approval flow compatible with testnet.
    """
    token_in = plan.token_in_address if plan.token_in_address else "0x0000000000000000000000000000000000000000"

    if plan.token_in == "ETH":
        amount_raw = _amount_to_raw(plan.amount_in, 18)
    else:
        amount_raw = plan.amount_in_raw or _amount_to_raw(plan.amount_in, 18)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": uniswap_api_key,
        "x-permit2-disabled": "true",          # use direct approval, simpler for agents
        "x-universal-router-version": "2.0",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Quote
        quote_body = {
            "type": "EXACT_INPUT",
            "amount": amount_raw,
            "tokenIn": token_in,
            "tokenOut": plan.token_out_address,
            "tokenInChainId": chain_id,
            "tokenOutChainId": chain_id,
            "swapper": wallet_address,
            "slippageTolerance": float(plan.slippage * 100),  # numeric, e.g. 0.5 for 0.5%
        }
        resp = await client.post(f"{UNISWAP_API}/quote", json=quote_body, headers=headers)
        if resp.status_code != 200:
            return TxResult(status="failure", error=f"Quote failed {resp.status_code}: {resp.text[:500]}")
        quote_data = resp.json()
        quote_obj = quote_data.get("quote", quote_data)

        # 2. Check / execute approval for ERC-20 input tokens
        if plan.token_in != "ETH" and plan.token_in_address:
            approval_body = {
                "token": plan.token_in_address,
                "amount": amount_raw,
                "walletAddress": wallet_address,
                "chainId": chain_id,
            }
            approval_resp = await client.post(
                f"{UNISWAP_API}/check_approval", json=approval_body, headers=headers
            )
            if approval_resp.status_code == 200:
                approval_data = approval_resp.json()
                if approval_data.get("approval"):
                    appr_tx = approval_data["approval"]
                    nonce = w3.eth.get_transaction_count(wallet_address)
                    signed_appr = w3.eth.account.sign_transaction(
                        {
                            "to": Web3.to_checksum_address(appr_tx["to"]),
                            "data": appr_tx["data"],
                            "value": 0,
                            "gas": int(appr_tx.get("gasLimit", 100_000)),
                            "gasPrice": w3.eth.gas_price,
                            "nonce": nonce,
                            "chainId": chain_id,
                        },
                        private_key,
                    )
                    appr_hash = w3.eth.send_raw_transaction(signed_appr.raw_transaction)
                    w3.eth.wait_for_transaction_receipt(appr_hash, timeout=120)

        # 3. Build swap calldata
        swap_resp = await client.post(
            f"{UNISWAP_API}/swap",
            json={"quote": quote_obj, "simulateTransaction": False},
            headers=headers,
        )
        if swap_resp.status_code != 200:
            return TxResult(status="failure", error=f"Swap build failed {swap_resp.status_code}: {swap_resp.text[:500]}")
        swap_data = swap_resp.json()

        # Response can be { "swap": { ... } } or the tx object directly
        tx_data = swap_data.get("swap", swap_data)

        # 4. Sign and broadcast
        raw_value = tx_data.get("value", "0")
        if isinstance(raw_value, str) and raw_value.startswith("0x"):
            value = int(raw_value, 16)
        else:
            value = int(raw_value or 0)

        gas_limit = tx_data.get("gasLimit") or tx_data.get("gas")
        tx_params = {
            "to": Web3.to_checksum_address(tx_data["to"]),
            "data": tx_data["data"],
            "value": value,
            "gas": int(gas_limit) if gas_limit else 400_000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(wallet_address),
            "chainId": chain_id,
        }
        signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        status = "success" if receipt["status"] == 1 else "failure"
        hash_str = _normalize_tx_hash(tx_hash)
        return TxResult(
            hash=hash_str,
            status=status,
            block_number=receipt["blockNumber"],
            gas_used=receipt["gasUsed"],
            amount_out=_extract_amount_out(quote_obj),
        )


async def execute_swap_bankr(plan: Plan, bankr_api_key: str) -> TxResult:
    """Execute a swap via Bankr Agent API (mainnet only, prompt-based)."""
    prompt = (
        f"Swap {plan.amount_in} {plan.token_in} to {plan.token_out} on Base. "
        f"Use slippage tolerance of {plan.slippage * 100:.1f}%."
    )
    headers = {"Content-Type": "application/json", "X-API-Key": bankr_api_key}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{BANKR_API}/agent/prompt",
            json={"prompt": prompt, "chain": "base"},
            headers=headers,
        )
        if resp.status_code != 200:
            return TxResult(status="failure", error=f"Bankr prompt failed {resp.status_code}: {resp.text[:400]}")

        job_data = resp.json()
        job_id = job_data.get("jobId") or job_data.get("id", "")

        for _ in range(30):
            await asyncio.sleep(2)
            status_resp = await client.get(f"{BANKR_API}/agent/job/{job_id}", headers=headers)
            if status_resp.status_code != 200:
                continue
            job = status_resp.json()
            job_status = job.get("status", "")
            if job_status == "completed":
                result = job.get("result", {})
                return TxResult(
                    hash=result.get("txHash", result.get("transactionHash", "")),
                    status="success",
                    amount_out=str(result.get("amountOut", "")),
                )
            if job_status == "failed":
                error = job.get("error", job.get("reason", "Unknown Bankr error"))
                sentinel_note = " (Sentinel rejection — do NOT override)" if "sentinel" in str(error).lower() else ""
                return TxResult(status="failure", error=f"Bankr: {error}{sentinel_note}")

        return TxResult(status="failure", error="Bankr job timed out after 60 seconds")


def execute_swap_dry_run(plan: Plan) -> TxResult:
    """Simulated swap — no real transaction."""
    return TxResult(hash="0x" + "0" * 64, status="success", block_number=0, gas_used=185_000, amount_out="simulated")
