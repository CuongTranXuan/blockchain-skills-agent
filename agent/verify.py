from __future__ import annotations

from web3 import Web3

from agent.types import Plan, TxResult, Verification


def verify_outcome(tx_result: TxResult, plan: Plan, w3: Web3) -> Verification:
    """Verify the transaction outcome against the original plan (skill-validate post-tx)."""
    if tx_result.status == "failure":
        return Verification(
            confirmed=False,
            matches_intent=False,
            details=f"Transaction failed: {tx_result.error}",
        )

    if tx_result.hash.startswith("0x" + "0" * 63):
        return Verification(
            confirmed=True,
            matches_intent=True,
            actual_amount_out="simulated",
            details="Dry-run mode — no real transaction to verify",
        )

    try:
        receipt = w3.eth.get_transaction_receipt(tx_result.hash)
    except Exception as e:
        return Verification(
            confirmed=False,
            matches_intent=False,
            details=f"Could not get receipt: {e}",
        )

    confirmed = receipt["status"] == 1
    block_number = receipt["blockNumber"]

    if not confirmed:
        revert_reason = _get_revert_reason(tx_result.hash, w3)
        return Verification(
            confirmed=False,
            matches_intent=False,
            block_number=block_number,
            details=f"Transaction reverted. Reason: {revert_reason}",
        )

    transfer_events = _parse_transfer_events(receipt)
    matches = _check_intent_match(transfer_events, plan)

    return Verification(
        confirmed=True,
        matches_intent=matches,
        actual_amount_out=tx_result.amount_out,
        block_number=block_number,
        details="Outcome verified against intent" if matches else "Outcome may differ from intent — review transfer events",
    )


def _get_revert_reason(tx_hash: str, w3: Web3) -> str:
    """Attempt to extract the revert reason by replaying the tx."""
    try:
        tx = w3.eth.get_transaction(tx_hash)
        w3.eth.call(
            {"to": tx["to"], "data": tx["input"], "value": tx["value"], "from": tx["from"]},
            tx["blockNumber"] - 1,
        )
        return "unknown (replay succeeded)"
    except Exception as e:
        msg = str(e)
        if "revert" in msg.lower() or "execution reverted" in msg.lower():
            return msg
        return f"unknown ({msg[:200]})"


def _parse_transfer_events(receipt: dict) -> list[dict]:
    """Extract ERC-20 Transfer events from receipt logs."""
    TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    transfers = []
    for log_entry in receipt.get("logs", []):
        topics = [t.hex() if isinstance(t, bytes) else str(t) for t in log_entry.get("topics", [])]
        if topics and topics[0] == TRANSFER_TOPIC and len(topics) >= 3:
            transfers.append({
                "token": log_entry["address"],
                "from": "0x" + topics[1][-40:],
                "to": "0x" + topics[2][-40:],
                "value": int(log_entry["data"].hex() if isinstance(log_entry["data"], bytes) else log_entry["data"], 16),
            })
    return transfers


def _check_intent_match(transfers: list[dict], plan: Plan) -> bool:
    """Basic check that at least one transfer matches the expected output token."""
    if not transfers:
        return True  # native ETH swap may not have ERC-20 transfers
    if plan.token_out_address:
        target = plan.token_out_address.lower()
        return any(t["token"].lower() == target for t in transfers)
    return True
