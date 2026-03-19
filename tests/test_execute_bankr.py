"""Tests for Bankr execution path."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.execute import _normalize_tx_hash, execute_swap_bankr, execute_swap_dry_run
from agent.types import Plan


def _plan() -> Plan:
    return Plan(
        action="swap", token_in="ETH", token_in_address="",
        token_out="USDC", token_out_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        amount_in=0.001, slippage=0.005, chain_id=8453,
    )


@pytest.mark.asyncio
async def test_bankr_success():
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"jobId": "j123"}

    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "status": "completed",
        "result": {"txHash": "0xabc", "amountOut": "25000000"},
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_post_response
    mock_client.get.return_value = mock_get_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("agent.execute.httpx.AsyncClient", return_value=mock_client):
        result = await execute_swap_bankr(_plan(), "test-key")
    assert result.status == "success"
    assert result.hash == "0xabc"


@pytest.mark.asyncio
async def test_bankr_sentinel_rejection():
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"jobId": "j456"}

    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "status": "failed",
        "error": "Sentinel blocked: suspicious contract",
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_post_response
    mock_client.get.return_value = mock_get_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("agent.execute.httpx.AsyncClient", return_value=mock_client):
        result = await execute_swap_bankr(_plan(), "test-key")
    assert result.status == "failure"
    assert "Sentinel" in result.error


@pytest.mark.asyncio
async def test_bankr_prompt_failure():
    mock_post_response = MagicMock()
    mock_post_response.status_code = 401
    mock_post_response.text = "Unauthorized"

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_post_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("agent.execute.httpx.AsyncClient", return_value=mock_client):
        result = await execute_swap_bankr(_plan(), "bad-key")
    assert result.status == "failure"
    assert "401" in result.error


def test_normalize_tx_hash_prefixes_bytes_and_strings():
    assert _normalize_tx_hash(bytes.fromhex("ab" * 32)) == "0x" + ("ab" * 32)
    assert _normalize_tx_hash("abc123") == "0xabc123"
    assert _normalize_tx_hash("0xabc123") == "0xabc123"
