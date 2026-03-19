# skill-validate — Transaction Validation

## When to use this skill

**Always.** Load this skill before and after any on-chain transaction. It defines how to validate intent before signing and verify outcomes after execution.

---

## Pre-transaction validation checklist

Before signing or submitting ANY transaction, check every item. If any check fails, follow the decision in the rightmost column.

| # | Check | How to verify | If fails |
|---|-------|--------------|----------|
| 1 | **Intent match** | Does the transaction payload match what was requested? (correct function, correct token addresses, correct amounts) | **BLOCK** — do not sign. Report mismatch to human. |
| 2 | **Decimals correct** | Are amounts in the correct unit? ETH uses 18 decimals. USDC uses 6. WBTC uses 8. Convert between human-readable and raw: `raw = human * 10^decimals`. Always verify the token's `decimals()` on-chain — never assume. | **BLOCK** — wrong decimals cause catastrophic loss (e.g., sending 1M tokens instead of 1). |
| 3 | **Balance sufficient** | Does the wallet hold enough of the input token to cover the amount PLUS gas? For native ETH: `balance >= amount + estimatedGas * gasPrice`. For ERC-20: check both token balance and ETH for gas. | **BLOCK** — transaction will revert. |
| 4 | **Allowance sufficient** | For ERC-20 swaps: does the spender contract (e.g., Uniswap router, Permit2) have enough allowance? Call `allowance(owner, spender)`. | **WARN** — need an approval tx first. Include approval in the execution plan. |
| 5 | **Slippage within bounds** | Is `minAmountOut` (or equivalent) within acceptable range? Default max slippage: 1% for stablecoins, 3% for volatile pairs, 5% absolute maximum. | **WARN** if >3%, **BLOCK** if >5%. |
| 6 | **Chain ID correct** | Does the transaction target the expected chain? Base Mainnet = 8453. Base Sepolia = 84532. Ethereum Mainnet = 1. | **BLOCK** — wrong chain means lost funds. |
| 7 | **Recipient valid** | Is the `to` address a known contract (DEX router, token contract) or the intended recipient? Not the zero address. Not the token contract itself (common mistake). | **WARN** if unknown address. **BLOCK** if zero address or self-send of ERC-20 to the token contract. |
| 8 | **Value within safety limit** | Is the USD value of the transaction within the agent's configured maximum (`maxTransactionValueUSD` in agent.json)? | **BLOCK** if above limit. Notify human for approval. |
| 9 | **Quote freshness** | Was the quote obtained recently? Quotes older than 30 seconds may have stale prices. Check the quote timestamp or block number vs current. | **WARN** — re-fetch quote before proceeding. |
| 10 | **Gas reasonable** | Is the estimated gas cost reasonable for this type of transaction? A simple transfer should be ~21K gas. A swap should be ~150K-300K. Orders of magnitude off suggest a problem. | **WARN** if gas seems abnormal. |

### Decision summary

- **PROCEED**: All checks pass.
- **WARN**: Some checks raised warnings but no blockers. Log the warnings, proceed with caution, notify human.
- **BLOCK**: At least one critical check failed. Do NOT sign or submit. Log the reason and notify human immediately.

---

## Post-transaction verification

After a transaction is submitted and confirmed, verify the outcome:

### Step 1 — Confirm inclusion

1. Get the transaction receipt using the tx hash.
2. Check `receipt.status`:
   - `1` = success — proceed to Step 2.
   - `0` = reverted — go to skill-debug to diagnose.
3. If no receipt after 60 seconds, the tx may be pending or dropped. Check if the nonce has been consumed. If not, the tx may need resubmission with higher gas.

### Step 2 — Parse events

1. Look for relevant events in the receipt logs:
   - **Transfer** events: `Transfer(from, to, value)` — verify the token, sender, recipient, and amount.
   - **Swap** events (Uniswap): verify `amountIn`, `amountOut`, token addresses match the intent.
2. Decode event data using the token/contract ABI.

### Step 3 — Compare to intent

1. Does the actual `amountOut` match the expected minimum from the quote (accounting for slippage)?
2. Did the tokens go to the correct recipient?
3. Was the correct token swapped (not a different token with a similar name)?

### Step 4 — Log and report

1. Log the verification result to `agent_log.json` with status `success` or `failure`.
2. If verification fails (amounts don't match, wrong recipient), notify the human immediately with:
   - What was expected vs what happened
   - The tx hash for manual inspection
   - A link to the block explorer: `https://basescan.org/tx/<txHash>`

---

## Provider-specific validation

### Uniswap Trading API

**Before swap:**
1. Call `/quote` — get `amountOut`, `gasEstimate`, `route`.
2. Validate: does the quoted `amountOut` make sense given current market price? (Sanity check: if swapping 0.01 ETH, expect roughly $25-35 USDC at typical prices. If the quote says $0.01 or $10,000, something is wrong.)
3. Call `/check_approval` — verify the wallet has approved Permit2/router.
4. If approval needed: submit approval tx first, wait for confirmation, then proceed.
5. Call `/swap` — get the transaction data.
6. Apply the full pre-tx checklist above to the swap transaction.

**After swap:**
1. Parse the Swap event from the receipt.
2. Verify `amountOut >= minAmountOut` from the original quote.
3. Log the actual execution price vs quoted price.

### Bankr

**Before execution:**
1. Bankr's Sentinel checks every transaction for malicious contracts, phishing, and unusual patterns.
2. Our validation adds on top of Sentinel: intent match, decimal checks, balance checks, human notification.
3. When Sentinel rejects a transaction, do NOT override. Log the rejection and notify the human.

**After execution:**
1. Use Bankr wallet/transaction visibility to confirm the outcome.
2. Apply the same post-tx verification (receipt, events, amount comparison).

---

## Common decimal reference

| Token | Decimals | 1 human unit in raw |
|-------|----------|-------------------|
| ETH | 18 | 1000000000000000000 |
| WETH | 18 | 1000000000000000000 |
| USDC | 6 | 1000000 |
| USDT | 6 | 1000000 |
| DAI | 18 | 1000000000000000000 |
| WBTC | 8 | 100000000 |

**Rule:** NEVER assume decimals. Always call `decimals()` on the token contract to verify. Some tokens have non-standard decimals.
