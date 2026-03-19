# skill-adapt — Multi-Provider Adaptation

## When to use this skill

Load this skill when interacting with a specific provider (Uniswap, Bankr) or querying chain state (Base RPC). It describes how to adapt the same reasoning pattern to different tools and backends.

---

## Universal pattern

Regardless of provider, every operation follows the same flow:

```
1. QUOTE   — get current price/state from the provider
2. VALIDATE — apply skill-validate pre-tx checklist
3. EXECUTE  — build and submit the transaction
4. VERIFY   — apply skill-validate post-tx verification
5. LOG      — record the result in agent_log.json
```

If any step fails, apply skill-debug.

---

## Base RPC (direct chain queries)

Use the chain's RPC endpoint for portfolio reads, balance checks, and transaction receipts. This works with any web3 library.

**Base Mainnet RPC:** `https://mainnet.base.org` (chain ID: 8453)
**Base Sepolia RPC:** `https://sepolia.base.org` (chain ID: 84532)
**Block explorer:** `https://basescan.org`

### Reading ETH balance

```
Call: eth_getBalance(address, "latest")
Result: balance in wei (18 decimals)
Human-readable: balance / 10^18
```

### Reading ERC-20 balance

```
Call: contract.balanceOf(address)
Result: balance in token's smallest unit
Then: contract.decimals() to get the decimal count
Human-readable: balance / 10^decimals
```

### Key token addresses on Base

| Token | Address | Decimals |
|-------|---------|----------|
| WETH | 0x4200000000000000000000000000000000000006 | 18 |
| USDC | 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 | 6 |
| USDT | 0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2 | 6 |
| DAI | 0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb | 18 |

### Getting transaction receipt

```
Call: eth_getTransactionReceipt(txHash)
Check: receipt.status == 1 (success) or 0 (revert)
Parse: receipt.logs for Transfer/Swap events
```

### Chain awareness

Before any operation, verify:
1. The RPC endpoint matches the intended chain (Base = 8453).
2. Token addresses are correct for that chain (USDC on Base != USDC on Ethereum).
3. Gas estimation uses the correct chain's gas oracle.

---

## Uniswap Trading API

**Base URL:** `https://trade-api.gateway.uniswap.org/v1`
**Auth:** `x-api-key` header with your Uniswap Developer Platform API key.

### Swap flow

#### Step 1: Get a quote

```
POST /quote
Body: {
  "tokenIn": "<token address or 'ETH'>",
  "tokenOut": "<token address>",
  "amount": "<amount in smallest unit (wei for ETH, raw for ERC-20)>",
  "type": "EXACT_INPUT",
  "chain": "base",
  "swapper": "<wallet address>",
  "slippageTolerance": "0.5"
}
Header: x-api-key: <your key>
```

Response includes: `quote.amountOut`, `quote.gasEstimate`, routing info.

**Validation:** Apply skill-validate checks — is `amountOut` reasonable? Is slippage within bounds? Is the quote fresh?

#### Step 2: Check approval

```
POST /check_approval
Body: {
  "token": "<tokenIn address>",
  "amount": "<amount in smallest unit>",
  "chain": "base",
  "walletAddress": "<wallet address>"
}
```

If approval is needed: the response contains the approval transaction. Submit it, wait for confirmation, then proceed.

For native ETH swaps: no approval needed.

#### Step 3: Execute swap

```
POST /swap
Body: { "quote": <the quote object from Step 1> }
```

Response includes: transaction data (`to`, `data`, `value`, `gasLimit`).

Sign and submit this transaction via web3. Apply skill-validate pre-tx checklist one final time before signing.

#### Step 4: Verify

After the transaction is confirmed, apply skill-validate post-tx verification: check receipt status, parse Swap events, compare actual amountOut to quoted minimum.

### Error codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request (malformed params) | Fix params, retry |
| 401 | Unauthorized (bad API key) | Check API key |
| 403 | Forbidden | Check API key permissions |
| 404 | Route not found | Token pair may not have liquidity; try different pair |
| 409 | Conflict | Retry after short delay |
| 422 | Validation error (bad token, bad amount) | Check token addresses and amounts; see error body for details |
| 429 | Rate limited | Back off; retry after Retry-After header |

---

## Bankr

**Docs:** https://docs.bankr.bot/getting-started/overview
**Purpose:** Financial rails for AI agents — wallet creation, DeFi operations, Sentinel security.

### Key capabilities

- **Agent wallet:** Gas-sponsored wallet for the agent. No need to manage ETH for gas.
- **DeFi operations:** Swaps, DCA, limit orders via natural language or API.
- **Sentinel:** Checks every transaction for malicious contracts, phishing, unusual patterns, prompt injection. Works alongside our skill-validate.
- **LLM Gateway:** OpenAI-compatible API for agent reasoning. Can be used as the LLM backend.

### Using Bankr with these skills

1. **Wallet:** Use Bankr wallet as the agent's execution wallet. Bankr sponsors gas.
2. **Swaps:** Use Bankr's DeFi API for swaps. Still apply skill-validate before and after.
3. **Sentinel:** Let Sentinel run its checks. Our skills add intent validation, decimal checks, and human notification on top.
4. **LLM Gateway:** Use Bankr Gateway (OpenAI-compatible) as the reasoning backend. Same `openai` library, different `base_url`.

### Pattern when using Bankr

```
1. Create or load Bankr wallet
2. Plan operation using LLM (Bankr Gateway or OpenAI)
3. Apply skill-validate pre-tx checks
4. Submit via Bankr API (Sentinel checks automatically)
5. If Sentinel rejects: do NOT override. Log and notify human.
6. If Sentinel approves and tx succeeds: apply skill-validate post-tx verification
7. Log everything
```

---

## Adapting to new providers

These skills are designed to be provider-agnostic. To add a new provider:

1. The universal pattern stays the same (quote -> validate -> execute -> verify -> log).
2. Add a provider-specific section in this file with endpoint URLs, auth, and flow.
3. Map the provider's error codes to skill-debug patterns.
4. All skill-validate checks still apply — they are provider-independent.
