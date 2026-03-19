# Research Report: Agent Framework Comparison for Autonomous Blockchain/DeFi Agent

**Date:** 2026-03-17
**Context:** Synthesis hackathon, 4 days remaining. Building autonomous agent on Base (Ethereum L2).

## Executive Summary

**Recommendation: Python custom agent (web3.py + OpenAI SDK + simple loop).** Not a framework. Not Node.js. Here's why.

After evaluating 5 approaches against hackathon constraints (4 days, real DeFi txs on Base, Protocol Labs loop, structured logs), the clear winner is a **lean Python script** with web3.py + OpenAI SDK. Frameworks (Google ADK, LangChain, CrewAI) add overhead without solving the actual hard problems (blockchain interactions, decimal handling, tx verification). Node.js has better web3 libs but worse AI ecosystem, and both Bankr + Uniswap expose REST APIs, making the web3 library advantage marginal.

The design doc currently says "Node.js/TypeScript" for the demo agent. **This should be reconsidered.** Python offers faster prototyping, better AI tooling, and sufficient web3 support for a hackathon demo. The skills themselves remain runtime-agnostic regardless.

## Comparative Analysis

### Scoring Matrix (1-5, higher = better for this hackathon)

| Criterion | Google ADK | LangChain/LangGraph | CrewAI | Node.js Custom | **Python Custom** |
|---|---|---|---|---|---|
| Web3/blockchain ecosystem | 2 | 2 | 1 | **5** | 3 |
| Agent loop quality | 4 | 4 | 3 | 3 | **4** |
| Hackathon speed (4 days) | 2 | 2 | 2 | 4 | **5** |
| Low overhead/complexity | 3 | 1 | 2 | **4** | **5** |
| LLM integration | 4 | 4 | 4 | 4 | **5** |
| Structured output | 3 | 3 | 3 | 4 | **5** |
| **TOTAL** | **18** | **16** | **15** | **24** | **27** |

---

## Framework-by-Framework Analysis

### 1. Google ADK (Python) — Score: 18/30

**What it is:** Google's open-source "code-first" agent toolkit. 18.4K GitHub stars, v1.27.1, Apache 2.0.

**Strengths:**
- Mature framework with LoopAgent, SequentialAgent, ParallelAgent built-in
- Custom tools via `@register_tool` decorator — trivial to wrap web3.py calls
- OpenAI-compatible via LiteLLM (not just Gemini)
- MCP integration for tool discovery
- Dev UI for debugging (`adk web`)

**Weaknesses for this hackathon:**
- **No blockchain examples exist.** Zero community precedent for DeFi agents on ADK.
- **Optimized for Gemini.** OpenAI support works via LiteLLM but it's a second-class path. Bankr's LLM Gateway is OpenAI-compatible format — adds unnecessary translation layer.
- **Framework overhead.** ADK enforces project structure (`adk create`), agent definitions, tool registries. For a 5-file agent doing one loop, this is ceremony, not value.
- **LoopAgent is rigid.** It loops agent execution, but our loop is discover→plan→execute→verify→log — a custom sequence, not a generic "repeat until done." Easier to write a `while True` loop.
- **Debugging tax.** When something breaks in the blockchain interaction, you're debugging through ADK's abstraction layer + LiteLLM + your code. Three layers deep.

**Verdict:** Good framework for enterprise multi-agent systems. Overkill for a hackathon single-agent with a custom loop. The LoopAgent doesn't map to the Protocol Labs loop pattern.

---

### 2. LangChain/LangGraph (Python) — Score: 16/30

**What it is:** Most popular agent framework. LangGraph = low-level graph-based orchestration. New "Deep Agents" runtime released March 2026.

**Strengths:**
- Graph-based architecture (nodes + edges + state) genuinely powerful for complex workflows
- Built-in persistence, streaming, human-in-the-loop
- Deep Agents (March 2026) adds planning via `write_todos`, subagent spawning
- Massive community; most tutorials/examples use LangChain
- LangSmith for observability

**Weaknesses for this hackathon:**
- **Abstraction hell.** LangChain is famously over-abstracted. To call a simple API, you go through: LangChain → Tool → Schema → Executor → Result parser. A `requests.post()` does the same thing in one line.
- **No blockchain integrations.** Search found zero DeFi/web3 examples in LangGraph.
- **The graph model doesn't help here.** Our loop is linear: discover→plan→execute→verify→log. Not a complex graph. A `for phase in phases:` loop is simpler and more debuggable.
- **Deep Agents is brand new** (released March 15, 2026 — 2 days ago). Risky for a hackathon.
- **Debugging nightmare.** LangChain error traces are notoriously deep and unhelpful.
- **Dependency bloat.** LangChain pulls in dozens of sub-packages. Version conflicts are common.

**Verdict:** The "enterprise hammer" for an "MVP nail." The framework's abstractions don't solve any problem we actually have. They create new ones.

---

### 3. CrewAI (Python) — Score: 15/30

**What it is:** Multi-agent orchestration platform. 450M+ monthly workflows, 60% of Fortune 500.

**Strengths:**
- Clean `@tool` decorator for custom tools
- MCP support for tool servers
- Enterprise features (monitoring, guardrails, RBAC)
- Task-based approach maps loosely to our phases

**Weaknesses for this hackathon:**
- **Multi-agent framework for a single-agent problem.** We have ONE agent doing ONE loop. CrewAI's value prop is coordination between multiple specialized agents. We don't need that.
- **Crew/Agent/Task abstractions add overhead.** You define a Crew, populate it with Agents, give them Tasks, set a Process. For a single loop, this is pure ceremony.
- **No blockchain examples.** Zero DeFi community content.
- **Enterprise-focused.** Serverless containers, RBAC, workflow tracing — none of this matters for a hackathon demo.
- **Opaque execution.** When things go wrong inside a Crew execution, debugging is harder than in plain Python.

**Verdict:** Wrong tool entirely. Using CrewAI for a single-agent DeFi demo is like using Kubernetes to deploy a shell script.

---

### 4. Node.js/TypeScript Custom — Score: 24/30

**What it is:** DIY agent with ethers.js/viem + OpenAI SDK.

**Strengths:**
- **Best web3 ecosystem.** viem is the gold standard: TypeScript-first, tree-shakeable, 2-3x faster than ethers.js. Official Uniswap SDKs are TypeScript.
- **Type safety.** TypeScript catches decimal/address errors at compile time. Critical for DeFi.
- **Uniswap official SDKs** (v3-sdk) are TypeScript, support Base (ChainId 8453).
- **OpenAI SDK** for Node.js is excellent; structured outputs via `response_format: { type: "json_object" }` works great.
- **No framework overhead.** You own every line.
- **Existing design decision.** Current design doc says Node.js/TypeScript.

**Weaknesses for this hackathon:**
- **AI ecosystem is weaker.** All major agent frameworks are Python-first. If you need to add LangChain tools, RAG, or complex prompting patterns, Python has better libraries.
- **Uniswap and Bankr APIs are REST.** You don't actually need the TypeScript SDKs — a `fetch()` call works. This diminishes the Node.js web3 advantage.
- **Slower prototyping** than Python for LLM-heavy code. TypeScript requires more boilerplate (types, interfaces, async/await ceremony).
- **web3 library advantage is marginal** when primary interactions are through Bankr API (REST) and Uniswap Trading API (REST). Direct contract calls via viem are a backup, not the primary path.

**Verdict:** Strong choice, especially if you're more comfortable with TypeScript. But the web3 library advantage is less relevant than it appears — Bankr and Uniswap both expose REST APIs.

---

### 5. Python Custom (web3.py + OpenAI SDK) — Score: 27/30 ★ RECOMMENDED

**What it is:** DIY agent in ~200 lines of Python.

**Strengths:**
- **Fastest hackathon velocity.** Python is the fastest path from "nothing" to "working demo." No compile step, no type definitions needed, REPL for testing.
- **Best LLM integration.** OpenAI Python SDK is the primary SDK; every example, tutorial, and guide is Python-first. Structured outputs, function calling, JSON mode — all work best here.
- **Bankr LLM Gateway** is OpenAI-compatible. Python `openai` package works directly:
  ```python
  from openai import OpenAI
  client = OpenAI(base_url="https://llm.bankr.bot", api_key="...")
  ```
- **web3.py is sufficient.** For reading balances, checking tx receipts, and calling contracts on Base — web3.py handles all of it. Not as elegant as viem, but functional.
- **uniswap-python** exists as a community wrapper (make_trade, get_price, etc.). Or just call the Uniswap Trading API via `requests`.
- **Zero framework overhead.** The "framework" is a while loop:
  ```python
  while True:
      portfolio = discover(w3, address)
      plan = llm_reason(portfolio, skills)
      if plan.action:
          result = execute(plan)
          verify(result)
      log_entry(agent_log, entry)
  ```
- **Structured output is native.** Python dicts → JSON. Pydantic for validation if needed. Writing agent_log.json is `json.dump()`.
- **Debugging is trivial.** Print statements, pdb, ipython. No framework abstractions to dig through.

**Weaknesses:**
- **web3.py < viem/ethers.js** in DX. Type hints exist but aren't as tight as TypeScript.
- **No official Uniswap Python SDK.** The community wrapper (uniswap-python) exists but is less maintained than official TypeScript SDKs. However, the Uniswap Trading API is REST — callable from any language.
- **Contradicts current design doc.** Design says "Node.js/TypeScript." Switching to Python requires updating docs.

**Verdict:** Maximum hackathon velocity with minimum wasted effort. Every minute spent on framework setup is a minute not spent on the actual demo.

---

## Critical Insight: REST APIs Neutralize Language Lock-in

Both Bankr and Uniswap expose **REST/HTTP APIs**:

| Service | Integration Method | Language Dependency |
|---|---|---|
| Bankr Agent API | REST (submit prompt → poll job) | None |
| Bankr LLM Gateway | OpenAI-compatible REST | None |
| Uniswap Trading API | REST | None |
| Base RPC | JSON-RPC over HTTP | None |

This means the Node.js/TypeScript advantage (viem, official Uniswap SDK) is relevant **only for direct smart contract interactions** — which is the backup path, not the primary one. The primary path (Bankr API + Uniswap Trading API) works identically from Python.

---

## The "Simple Loop" Skeleton (Python)

This is the entire agent runtime. ~150 lines of real code:

```python
import json, time, uuid
from openai import OpenAI
from web3 import Web3

# Config
w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
llm = OpenAI(api_key="...", base_url="https://llm.bankr.bot")  # or direct OpenAI
AGENT_ADDRESS = "0x..."
SKILLS = open("skills/SKILL-INDEX.md").read()

agent_log = {
    "agent": "blockchain-skills-agent",
    "session": str(uuid.uuid4()),
    "erc8004": AGENT_ADDRESS,
    "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "entries": []
}

def log_entry(phase, action, skill, inp, out, status):
    agent_log["entries"].append({
        "id": len(agent_log["entries"]) + 1,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": phase, "action": action, "skill": skill,
        "input": inp, "output": out, "status": status
    })
    with open("agent_log.json", "w") as f:
        json.dump(agent_log, f, indent=2)

def discover():
    """Read portfolio on Base"""
    balance_wei = w3.eth.get_balance(AGENT_ADDRESS)
    balance_eth = w3.from_wei(balance_wei, "ether")
    # ... read ERC-20 balances via multicall
    return {"eth": float(balance_eth), "tokens": [...]}

def plan(portfolio):
    """LLM reasons about what to do"""
    response = llm.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SKILLS},
            {"role": "user", "content": f"Portfolio: {json.dumps(portfolio)}. What should we do?"}
        ]
    )
    return json.loads(response.choices[0].message.content)

def execute(plan):
    """Execute via Bankr API or Uniswap Trading API"""
    # requests.post("https://api.bankr.bot/...", json=plan)
    pass

def verify(tx_hash):
    """Verify tx on-chain"""
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    return {"confirmed": receipt.status == 1, "block": receipt.blockNumber}

# Main loop
for phase_fn, phase_name in [(discover, "discover"), (plan, "plan"), (execute, "execute"), (verify, "verify")]:
    result = phase_fn(...)  # simplified
    log_entry(phase_name, ...)
```

**That's it.** No framework. No abstractions. Full control. Fully debuggable.

---

## Recommendation

### Primary: Python Custom Agent

| Aspect | Decision |
|---|---|
| **Language** | Python 3.11+ |
| **LLM** | `openai` SDK → Bankr LLM Gateway (OpenAI-compatible) |
| **Blockchain** | `web3.py` for balance reads + tx verification |
| **DeFi** | Bankr Agent API (REST) + Uniswap Trading API (REST) |
| **Agent loop** | Simple while/for loop — no framework |
| **Logging** | `json.dump()` → agent_log.json |
| **Validation** | Pydantic models for structured I/O (optional) |

### Why Not Node.js?

The design doc says Node.js. Here's the honest trade-off:

| Factor | Node.js/TS | Python | Winner |
|---|---|---|---|
| Web3 lib quality | viem is superior | web3.py is adequate | Node.js |
| Uniswap SDK | Official TypeScript | Community Python wrapper | Node.js |
| OpenAI SDK quality | Good | Best (primary SDK) | Python |
| Prototyping speed | Moderate | Fast | Python |
| Structured JSON output | Needs interfaces | Dicts + json.dump | Python |
| Bankr API | REST (same) | REST (same) | Tie |
| Framework availability | Few agent frameworks | All major frameworks | Python |
| Debugging speed | TypeScript compilation | Instant | Python |

**If the team is more comfortable with TypeScript and already has boilerplate ready, stick with Node.js.** The difference isn't make-or-break. But for pure hackathon velocity with no existing code, Python wins.

### If You Choose Node.js Anyway

Use: `viem` (not ethers.js) + `openai` npm + `zod` for structured output validation. Skip all frameworks. Same simple loop pattern as the Python skeleton above, just in TypeScript.

---

## What NOT to Use

| Framework | Why Not |
|---|---|
| Google ADK | Good framework, wrong problem. LoopAgent doesn't map to Protocol Labs loop. Optimized for Gemini, not OpenAI. Zero blockchain examples. |
| LangChain/LangGraph | Abstraction overhead kills hackathon velocity. Debugging through framework layers wastes hours. Graph model doesn't help a linear loop. |
| CrewAI | Multi-agent framework for a single-agent problem. Pure overhead. |
| Deep Agents | Released 2 days ago (March 15). Too risky for a hackathon. |

---

## Unresolved Questions

1. **Bankr API key availability.** Need to confirm access and rate limits before committing to Bankr as primary execution layer.
2. **Uniswap Trading API access.** Need Developer Platform API key — application required.
3. **Team TypeScript vs Python comfort.** If team is significantly faster in TypeScript, the velocity argument flips.
4. **uniswap-python maintenance status.** If the community wrapper is broken for V3 on Base, may need to call REST API directly (which works in either language).
5. **Design doc update.** If switching from Node.js to Python, design doc needs revision.

---

*Sources: GitHub (google/adk-python, Uniswap/v3-sdk), Bankr docs (docs.bankr.bot), LangChain docs, CrewAI docs, MetaMask viem comparison, Real Python LangGraph tutorial, PkgPulse web3 library comparison, LambdaClass eth-agent blog.*
