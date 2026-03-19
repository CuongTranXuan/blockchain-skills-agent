from __future__ import annotations

from web3 import Web3

from agent.config import CHAIN_CONFIGS
from agent.types import Portfolio, TokenBalance

ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals",
     "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
]


def discover(w3: Web3, wallet_address: str) -> Portfolio:
    """Read the wallet's portfolio: native ETH + known ERC-20 tokens for the connected chain."""
    address = Web3.to_checksum_address(wallet_address)
    chain_id = w3.eth.chain_id
    tokens_map = CHAIN_CONFIGS.get(chain_id, {}).get("tokens", {})
    chain_name = CHAIN_CONFIGS.get(chain_id, {}).get("name", "unknown")

    tokens: list[TokenBalance] = []

    eth_balance = w3.eth.get_balance(address)
    tokens.append(TokenBalance(symbol="ETH", address="", balance_raw=eth_balance, decimals=18))

    for symbol, token_addr in tokens_map.items():
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
            balance = contract.functions.balanceOf(address).call()
            decimals = contract.functions.decimals().call()
            tokens.append(TokenBalance(symbol=symbol, address=token_addr, balance_raw=balance, decimals=decimals))
        except Exception:
            pass

    return Portfolio(chain=chain_name, chain_id=chain_id, address=address, tokens=tokens)
