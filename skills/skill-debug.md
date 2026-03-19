# skill-debug — Failure Diagnosis & Human Notification

## When to use this skill

Load this skill when a transaction fails, an API returns an error, or something unexpected happens. It helps diagnose the root cause and produce an actionable summary for the human.

---

## Diagnosis flowchart

When something goes wrong, follow this sequence:

```
1. IDENTIFY  — what failed? (tx revert, API error, unexpected result)
2. DIAGNOSE  — why did it fail? (check common causes below)
3. CLASSIFY  — is it recoverable? (retry, fix and retry, or escalate)
4. ACT       — retry, fix, or notify human
5. LOG       — record everything in agent_log.json
```

---

## Common failures and diagnosis

### Transaction reverted (receipt.status == 0)

| Possible cause | How to check | Fix |
|---------------|-------------|-----|
| **Insufficient balance** | Compare wallet balance to tx amount + gas | Wait for funds or reduce amount |
| **Insufficient allowance** | Call `allowance(owner, spender)` | Submit approval tx first |
| **Wrong decimals** | Compare amount in tx vs intended human amount * 10^decimals | Recalculate with correct decimals (call `decimals()` on the token) |
| **Slippage exceeded** | The price moved between quote and execution | Re-fetch quote with higher slippage tolerance (up to 5% max) |
| **Nonce conflict** | Check `eth_getTransactionCount` vs tx nonce | Use the correct nonce; if a pending tx is stuck, speed it up or cancel |
| **Gas too low** | Tx ran out of gas | Re-estimate gas; add 20% buffer |
| **Contract paused/restricted** | Some tokens or protocols pause transfers | Check contract state; notify human |

### Getting the revert reason

1. Call `eth_call` with the same transaction parameters to simulate it.
2. The error response often contains a revert reason string (e.g., "INSUFFICIENT_OUTPUT_AMOUNT", "ERC20: transfer amount exceeds balance").
3. Parse the revert reason and map it to the causes above.

### API errors

#### Uniswap Trading API

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check request body format; fix and retry |
| 401 | Unauthorized | API key invalid or expired; notify human |
| 403 | Forbidden | API key lacks permissions; notify human |
| 404 | No route found | Token pair has no liquidity on this chain; try a different pair or route |
| 409 | Conflict | Retry after 2-5 seconds |
| 422 | Validation error | Check token addresses (correct chain?), amounts (correct decimals?), and swapper address |
| 429 | Rate limited | Wait for `Retry-After` header duration; then retry |

#### Bankr

| Issue | Action |
|-------|--------|
| Sentinel rejection | Do NOT override. Log the rejection reason. Notify human: "Bankr Sentinel blocked this transaction because: [reason]. Please review." |
| Wallet creation failed | Check API key; check network connectivity; retry |
| Insufficient gas | Bankr sponsors gas, so this shouldn't happen. If it does, contact Bankr support. |

#### General HTTP errors

| Code | Action |
|------|--------|
| 5xx | Server error; retry with exponential backoff (2s, 4s, 8s); max 3 retries |
| Timeout | Network issue; retry; if persistent, switch to backup endpoint |
| Connection refused | Service is down; switch to fallback provider; notify human |

---

## Recovery classification

After diagnosing, classify the failure:

| Class | Meaning | Action |
|-------|---------|--------|
| **Auto-recoverable** | Can be fixed without human input (e.g., re-fetch quote, increase gas) | Fix and retry automatically. Max 3 retries. |
| **Needs human input** | Requires a decision (e.g., higher slippage tolerance, more funds) | Notify human with the specific decision needed. Pause execution. |
| **Unrecoverable** | Cannot be fixed (e.g., contract paused, Sentinel rejection) | Notify human with full context. Stop execution for this operation. |

---

## Human notification

### When to notify

ALWAYS notify the human for:
- Any transaction failure (even if auto-recovered — mention it happened)
- Transaction value above the safety limit
- Sentinel rejection
- Fraud signals (suspicious contract, drainer pattern, phishing)
- Any situation where the agent is unsure

### Notification format

```
[AGENT NOTIFICATION]

Status: SUCCESS / FAILURE / WARNING
Action: <what the agent was trying to do>
Result: <what actually happened>

Details:
- <specific information about what went right or wrong>
- <relevant tx hash, amounts, addresses>

Recommendation:
- <what the human should do, if anything>

Explorer: https://basescan.org/tx/<txHash>
```

### Examples

**Successful swap:**
```
Status: SUCCESS
Action: Swap 0.01 ETH -> USDC on Base via Uniswap
Result: Received 25.43 USDC (expected ~25.30 USDC minimum)

Details:
- Tx: 0xabc123...
- Slippage: 0.2% (within 0.5% tolerance)
- Gas used: 185,234 (~$0.003)

Explorer: https://basescan.org/tx/0xabc123...
```

**Failed swap:**
```
Status: FAILURE
Action: Swap 0.01 ETH -> USDC on Base via Uniswap
Result: Transaction reverted — slippage exceeded

Details:
- The price moved between quote and execution.
- Quoted: 25.43 USDC minimum. Actual: would have been 24.80 USDC.
- No funds were lost (tx reverted).

Recommendation:
- Retry with higher slippage tolerance (currently 0.5%, suggest 1.0%)
- Or wait for price to stabilize and try again
```

---

## Fraud and safety signals

Watch for these patterns and **BLOCK + notify human** immediately:

| Signal | What to look for |
|--------|-----------------|
| **Unlimited approval** | An approval tx that sets allowance to MAX_UINT256 for an unknown contract |
| **Unknown contract** | The `to` address is not a known DEX router, token, or protocol contract |
| **Fee-on-transfer token** | The received amount is significantly less than expected (token takes a fee on transfer) |
| **Rebase token** | Balance changes without a transfer event (rebasing tokens change balances automatically) |
| **Phishing contract** | Contract name or symbol mimics a known token but has a different address |
| **Drainer pattern** | Contract requests approval for all tokens or calls unexpected functions |

When any fraud signal is detected:
1. **BLOCK** the transaction — do not sign or submit.
2. Log the signal with full details.
3. Notify the human immediately with the signal type and evidence.
4. Do NOT retry without explicit human approval.
