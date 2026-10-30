# Jev API for `validation.judge`

Research for [Document the Jev API for validation.judge](https://github.com/DavillyDevTeam/mainart-stack/issues/5).
Read 2026-10-12 against TypeSafe first-party docs, blog, GitHub org, and this machine.
No product code.

**Gist.** Jev is TypeSafe AI's hosted System One model (not a product named "jav"). Official call is `POST https://api.typesafe.ai/v1/systemone` with `Authorization: Bearer <API_KEY>`. Input is `state` plus a map of typed questions (`choice` / `score` / `noul`); output is typed answers with probabilities (and a derived `confidence` on Choice/Score), never free text. Documented latency is 70–500 ms (most queries ~100 ms); list price is $0.042 per million input tokens, output free. A generic `validation.judge` capability can wrap that contract; playbooks should call the capability, never Jev. No first-party local weights or official MCP; none are installed on this machine.

Glossary (this repo): **module** = optional capability pack; **capability** = named slot such as `validation.judge`; Jev is a **provider** of that slot, not the slot. Router and playbooks call a capability, never a module by name.

---

## 1. "jav" is not a different product

The ticket asked whether "jav" is a different product. It is not.

- TypeSafe's first public System One model is **Jev**, named after William Stanley Jevons. ([Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev))
- Official domains: [typesafe.ai](https://typesafe.ai/), [docs.typesafe.ai](https://docs.typesafe.ai/llms.txt), [api.typesafe.ai](https://docs.typesafe.ai/api), [console.typesafe.ai](https://console.typesafe.ai/).
- Official GitHub org: [github.com/typesafe-ai](https://github.com/typesafe-ai). Public repos include SDKs, an agent skill, a System One LLM adapter, evals — no product named Jav.
- The current models table lists only `jev-1.13.0` plus aliases `jev-latest` and `jev-preview`. ([Models](https://docs.typesafe.ai/models.md))

Third-party mirrors (`jevtypesafeai.com`, `jevapi.dev`, `thejevai.com`) restate the same TypeSafe endpoint or proxy it. They are not the official API.

---

## 2. What Jev is (and is not)

Jev is TypeSafe's flagship **System One** model: unstructured **state** in, typed probabilistic decisions out. It does not generate text, write code, hold a conversation, or explain its reasoning. ([Introduction](https://docs.typesafe.ai/introduction.md), [System One](https://docs.typesafe.ai/concepts/system-one.md), [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents.md))

TypeSafe's own framing for a coding-agent host:

> Jev is **not** a drop-in replacement for the LLM behind Claude Code, Cursor, opencode, Copilot, Muse Spark, Grok Bot, or similar tools. ([coding-agents](https://docs.typesafe.ai/introduction/coding-agents.md))

That matches this repo's split: Jev is a **module provider** for a judge slot, not a host adapter and not the router.

"Can't hallucinate" in the launch post means **schema match is guaranteed** (the model cannot emit a label outside the supplied options). It does **not** mean every answer is semantically correct. Calibration is measured across groups of predictions; it does not guarantee an individual answer. ([launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [System One](https://docs.typesafe.ai/concepts/system-one.md), homepage hallucination table footnote on [typesafe.ai](https://typesafe.ai/))

---

## 3. Official API and auth

### Endpoint

```
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

([API reference](https://docs.typesafe.ai/api), [Quick start](https://docs.typesafe.ai/introduction/quickstart.md))

List models:

```
GET https://api.typesafe.ai/v1/models
Authorization: Bearer $TYPESAFE_API_KEY
```

Currently lists aliases; versioned IDs such as `jev-1.13.0` are accepted in `model` whether or not they appear. ([Models](https://docs.typesafe.ai/models.md))

### Auth

| Item | Official value |
| --- | --- |
| Header | `Authorization: Bearer <API_KEY>` |
| Env var | `TYPESAFE_API_KEY` (required for SDKs) |
| Key console | [console.typesafe.ai/keys](https://console.typesafe.ai/keys) (quick start); Python SDK also points at [console.typesafe.ai](https://console.typesafe.ai/) |
| Base URL env | `TYPESAFE_BASE_URL`, default `https://api.typesafe.ai` |
| Default model env | `TYPESAFE_DEFAULT_MODEL`, default `jev-latest` |
| 401 | Missing or invalid API key |

([Quick start](https://docs.typesafe.ai/introduction/quickstart.md), [Python constants](https://docs.typesafe.ai/sdk/python/api/constants.md), [Python usage / env](https://docs.typesafe.ai/sdk/python/usage.md), [JS `TypeSafeClientConfig`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TypeSafeClientConfig.md), [API errors](https://docs.typesafe.ai/api.md))

Python SDK strips leading/trailing whitespace from keys and rejects empty keys, internal whitespace, control characters, and non-ASCII before sending. An explicitly empty `api_key=` does not fall back to the environment. ([Python usage](https://docs.typesafe.ai/sdk/python/usage.md))

JS SDK: `apiKey` falls back to `TYPESAFE_API_KEY`; `dangerouslyAllowBrowser` defaults false (browser use would expose the key). Timeout default 10_000 ms. ([TypeSafeClientConfig](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TypeSafeClientConfig.md))

Python SDK default timeout is 10.0 seconds per HTTP operation. ([constants](https://docs.typesafe.ai/sdk/python/api/constants.md))

### Official clients

| Client | Install | Source |
| --- | --- | --- |
| Python 3.10+ | `pip install typesafe-sdk` / `uv add typesafe-sdk` | [docs](https://docs.typesafe.ai/sdk/python.md), [github.com/typesafe-ai/typesafe-sdk-python](https://github.com/typesafe-ai/typesafe-sdk-python) |
| JS/TS Node 20+ | `npm install @typesafe-ai/sdk` | [docs](https://docs.typesafe.ai/sdk/javascript.md), [github.com/typesafe-ai/typesafe-sdk-js](https://github.com/typesafe-ai/typesafe-sdk-js) |
| Agent skill (docs for coding agents, not a runtime) | `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`; or `npx skills add typesafe-ai/skills --skill typesafe-ai` | [Agent skill](https://docs.typesafe.ai/agent-skill.md), [github.com/typesafe-ai/skills](https://github.com/typesafe-ai/skills) |

SDKs call `client.system_one(...)` / `client.systemOne(...)` and default the model to `jev-latest`. ([Python SDK](https://docs.typesafe.ai/sdk/python.md), [JS SDK](https://docs.typesafe.ai/sdk/javascript.md))

### Documented gateways (same wire contract, different base URL / key)

TypeSafe documents pointing the official SDK at:

- OpenRouter: `base_url="https://openrouter.ai/api"`, `model="~typesafe/jev-latest"`, `OPENROUTER_API_KEY`
- Vercel AI Gateway: `base_url="https://ai-gateway.vercel.sh/typesafe"`, `model="typesafe-ai/jev"`, `AI_GATEWAY_API_KEY`
- Pydantic AI Gateway: `base_url="https://gateway-us.pydantic.dev/proxy/typesafe"`, `model="jev-latest"`, `PYDANTIC_AI_GATEWAY_API_KEY`

([Python usage — configuring the base URL](https://docs.typesafe.ai/sdk/python/usage.md))

### Errors

| Status | Meaning |
| --- | --- |
| 401 | Missing or invalid API key |
| 422 | Request body failed validation |
| 429 | Rate limit exceeded |
| 529 | TypeSafe temporarily overloaded |

Retry 429/529 with exponential backoff; SDKs do this by default and honor `retry-after` when present. ([API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md))

---

## 4. Input / output types: typed decision + probability, not free text

This is the property that makes Jev a fit for `validation.judge`.

### Request

Three top-level fields ([API](https://docs.typesafe.ai/api.md)):

| Field | Type | Role |
| --- | --- | --- |
| `state` | string \| object \| array | Content to judge. Text only. |
| `model` | string | e.g. `jev-latest` (alias) or `jev-1.13.0` (pin) |
| `questions` | map of id → Question | Typed questions; answers return under the same keys. The key is **not** sent to the model. |

`state` shapes ([State](https://docs.typesafe.ai/concepts/state.md), [Models](https://docs.typesafe.ai/models.md)):

- string — one message/passage
- object — named fields (preferred when there is more than one piece of context)
- array of text — a sequence of messages/records
- **not** image, audio, or video. Pre-process those to text first.

Questions may reference nested state with backticked paths such as `` `ticket.messages[0].text` ``. ([official skill](https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md), [primitives](https://docs.typesafe.ai/primitives.md))

### Three question primitives

All share `type` + `instructions`. `instructions` may be a string, object, or array. ([API](https://docs.typesafe.ai/api.md), [Primitives](https://docs.typesafe.ai/primitives.md))

| `type` | Asks | `criteria` | Answer |
| --- | --- | --- | --- |
| `noul` | Is this true? | optional `{ true, false }` glosses | `{ type, noul }` with `noul` in 0..1 = P(yes). **No** separate `confidence`. |
| `choice` | Which of these options? | map of option → description (or `null`); **max 255** options | `{ type, choice, probabilities, confidence }` |
| `score` | Where on this ordered rubric? | ordered array of level descriptions; **2–10** levels | `{ type, score, legend, probabilities, confidence }` |

Mix types in one request. Every question is evaluated **in parallel and in isolation** against the same state. Adding questions barely changes response time; it does consume tokens. ([Introduction](https://docs.typesafe.ai/introduction.md), [Primitives](https://docs.typesafe.ai/primitives.md))

### Example request (official API sample)

```json
{
  "state": "Help! My payouts have been failing for 3 days.",
  "model": "jev-latest",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "Does this convey urgency?",
      "criteria": {
        "true": "Explicitly time-sensitive",
        "false": "No urgency expressed"
      }
    },
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this?",
      "criteria": {
        "billing": "Payments, invoicing, refunds",
        "technical": "Bugs, outages, integrations",
        "sales": "Pricing, upgrades, new accounts"
      }
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated is the customer?",
      "criteria": ["Calm", "Frustrated", "Very angry"]
    }
  }
}
```

(composed from the three official examples on [API](https://docs.typesafe.ai/api.md))

### Example response

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "is_urgent": { "type": "noul", "noul": 0.95 },
    "department": {
      "type": "choice",
      "choice": "billing",
      "probabilities": { "billing": 0.88, "technical": 0.12, "sales": 0.0 },
      "confidence": 0.81
    },
    "frustration": {
      "type": "score",
      "score": 1.05,
      "legend": { "0": "Calm", "1": "Frustrated", "2": "Very angry" },
      "probabilities": { "0": 0.0, "1": 0.95, "2": 0.05 },
      "confidence": 0.92
    }
  },
  "usage": { "input_tokens": 318, "output_tokens": 34 }
}
```

(`score` is probability-weighted and **can land between levels**. `choice` is the highest-probability option. `probabilities` sum to 1. Response `model` is the **versioned** id that actually ran.) ([API](https://docs.typesafe.ai/api.md), [Models](https://docs.typesafe.ai/models.md))

### Probability vs confidence

- **Probability** is the distribution over options/levels (Choice/Score) or P(yes) (Noul).
- **Confidence** (Choice/Score only) is a 0..1 statistic of how peaked that distribution is: 1 = all mass on one outcome, 0 = even spread. It is **not** a second model, and it is **not** "permission to act" or overall workflow correctness. ([Confidence](https://docs.typesafe.ai/confidence.md), official [SKILL.md](https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md))
- Noul has no `confidence`; a value near 0.5 means similar probability for yes and no, not "medium intensity." (same sources)

TypeSafe's recommended pattern: high confidence → act; medium → confirm/review; low → do not act / escalate to a human or a reasoning model. Where to draw the lines is the application's job. ([Confidence](https://docs.typesafe.ai/confidence.md), [How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md))

There is **no free-text field** in the answer. If a playbook needs a written rationale, that is a different capability (an LLM), not Jev.

---

## 5. Latency and cost (first-party numbers only)

From [Models](https://docs.typesafe.ai/models.md) for **Jev 1.13 / `jev-1.13.0`**:

| Spec | Documented value |
| --- | --- |
| Price | **$42 / Btok**, **$0.042 / Mtok** of **input**. Output tokens are free. |
| Rate limits | 100K tokens/s and 80 requests/s. Over either → 429. Limits "are adjusting dynamically" and "can change without notice." Higher limits: `sales@typesafe.ai`. |
| Context | 64k tokens per request for state + all questions combined; 32k for state + the **single longest** question. State is ingested once; questions run in parallel. |
| Input | Text only |
| Customization | No customer fine-tune / LoRA. Same weights for every account. Shape answers via `state` / `instructions` / `criteria`. |
| Training data | "Jev is not trained on customer requests or responses." ZDR is an enterprise legal option. |

Latency, first-party (not third-party benches):

| Claim | Source |
| --- | --- |
| End-to-end **70 ms–500 ms** | [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) |
| **Most queries ~100 ms**; fast enough for real-time request paths and UIs | [How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one) |
| Homepage demo of one workflow: Jev **0.114 s / $0.000081** vs LLM **8.566 s / $0.013880** | [typesafe.ai](https://typesafe.ai/) |
| Headline **193.6× faster, 444.6× cheaper** vs LLMs on TypeSafe's own four workflow evals; they call this "the higher end of real world gains" | [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev), homepage proof link |
| Workflow eval site | [evals.typesafe.ai](https://evals.typesafe.ai/) |

SDK default timeout is 10 s, i.e. far above typical latency; treat 10 s as a client deadline, not a performance target. ([constants](https://docs.typesafe.ai/sdk/python/api/constants.md))

Language: English is the primary training language and currently the most accurate; other languages including CJK "are handled but not equally well." Test and watch confidence. ([Models](https://docs.typesafe.ai/models.md))

Jaggedness TypeSafe already documents for `jev-1.13` (relevant to a judge): literal reading of the question as written; not a calculator; not a text generator — forcing generation by chaining choices "will not work well and will be very slow." ([Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md))

---

## 6. Local install and MCP (this machine + first-party)

### First-party

| Surface | Exists? |
| --- | --- |
| Hosted HTTP API | Yes — this is the product. |
| Official Python / JS SDKs | Yes. They are HTTP clients, not a local model. |
| Official **agent skill** | Yes. Teaches a coding agent how to *write* TypeSafe integrations. Does not run Jev locally. ([Agent skill](https://docs.typesafe.ai/agent-skill.md), [docs.typesafe.ai/.well-known/agent-skills/type-safe/skill.md](https://docs.typesafe.ai/.well-known/agent-skills/type-safe/skill.md)) |
| Official **MCP server** | **No.** Not in [docs.typesafe.ai/llms.txt](https://docs.typesafe.ai/llms.txt), not in the [typesafe-ai GitHub org](https://github.com/typesafe-ai) (12 public repos, none named MCP). |
| Official local / open weights | **No.** Models page: same hosted weights for every account; no self-host docs. Launch post: early-access hosted service. |

Third-party `jev-mcp` repos exist (community wrappers around the hosted HTTP API). They are not TypeSafe products and were not used here.

TypeSafe *does* publish [`system-one-adapter-python`](https://github.com/typesafe-ai/system-one-adapter-python): a drop-in `system_one` client backed by OpenAI / Anthropic / Gemini instead of Jev. Same question/answer types, LLM underneath. That is an official **comparison adapter**, not a local Jev.

### This machine (checked 2026-10-12)

- No `TYPESAFE_API_KEY` / `JEV_*` in the environment.
- `typesafe_sdk` is not installed (`ModuleNotFoundError`).
- No `jev`, `jav`, or `typesafe` binary on `PATH`.
- Cursor MCP (`~/.cursor/mcp.json`) has only Notion. Claude / Grok configs have no TypeSafe or Jev MCP server.
- No local TypeSafe skill or Jev package in the agent skill dirs searched for this ticket.

A mainart-stack Jev **module** would therefore be a small HTTP (or official SDK) wrapper plus env config, not a bundled model.

---

## 7. How this implements `validation.judge` as an optional module

Map standing preference (issue 1): optional modules register capabilities; Jev is the first **provider** of `validation.judge`, never a hardcoded if-Jev. Issue 10 (capability registry) is waiting on this research so the slot fits a real provider.

### Fit

TypeSafe's documented use of Jev for judging LLM work is the same shape as a validation slot:

- Launch post use case: "Verify everything. Score, judge, verify, guardrail, and detect jailbreaks of LLM prompts, reasoning traces, and/or outputs." ([launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev))
- Cookbook **Double-checking citations**: deterministic string-match first, then one Choice (`supports` / `contradicts` / `says_nothing`) plus a confidence gate (`AUTO_ACCEPT = 0.8`) to auto-accept or send to a human. Returns stack-owned verdicts `verified` / `unsupported` / `contradicted` / `fabricated`. ([citation check](https://docs.typesafe.ai/cookbooks/citation_check.md))
- Cookbook **Guardrails for LLMs**: one request, threshold noul/score, pass / review / block / route. ([guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md))

Jev is **not** the judge prompt. Code owns the workflow; Jev answers narrow typed questions; code combines answers and applies thresholds. ([How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md))

### Recommended split (no product code — interface only)

```
playbook  ──calls──►  capability validation.judge
                              │
                     (if a module registered it)
                              ▼
              module (Jev provider)  ──HTTP──►  POST /v1/systemone
```

- **Playbooks / router** call `validation.judge`. They never name Jev, TypeSafe, `jev-latest`, or `TYPESAFE_API_KEY`.
- **Module** owns: base URL, API key, model id (pin `jev-1.13.0` once thresholds are tuned; log the response `model`), mapping from the capability I/O onto System One `state` + `questions`, retries on 429/529, timeout.
- **If no module registered the capability**: playbooks skip the judge or take the documented no-provider path (issue 10). Do not special-case Jev.

### Can a generic slot wrap it without naming Jev? Yes.

Two reasons, both first-party:

1. **The wire contract is already model-generic.** Every TypeSafe model is served by `POST /v1/systemone`; the `model` field selects the implementation. ([Models](https://docs.typesafe.ai/models.md)) Gateways keep the same body and swap URL/key/model id. ([Python usage](https://docs.typesafe.ai/sdk/python/usage.md))
2. **TypeSafe's own adapter proves a second provider can speak the same types.** [`system-one-adapter-python`](https://github.com/typesafe-ai/system-one-adapter-python) is a drop-in `system_one` client over LLM APIs, returning `typesafe_sdk.SystemOneResponse` answers. A later `validation.judge` provider could be Jev, that adapter, or anything that emits a typed decision + probability.

So the capability I/O should be **typed decision + probability**, not free text and not "whatever Jev returned as JSON." Concretely, a slot that another provider can fill:

**Input (capability, not vendor):**

- `state`: string | object | array of text (the thing under judgment, plus any policy/evidence the judge is allowed to see).
- `questions`: named map of `{ kind: "yes_no" | "choice" | "score", instructions, criteria? }`.

**Output (capability, not vendor):**

- `answers[id]`: either `{ kind: "yes_no", p_yes }` or `{ kind: "choice", winner, probabilities, confidence }` or `{ kind: "score", value, legend, probabilities, confidence }`.
- `usage`: input/output token counts when the provider reports them.
- `provider_model`: opaque string for logs (Jev would put `jev-1.13.0` here). Playbooks must not branch on it.

Mapping onto Jev is mechanical: `yes_no` → `noul`, `p_yes` → `noul`, `winner` → `choice`. The module performs that mapping. Playbooks never write `"type": "noul"`.

A **narrower** judge facade (single verdict enum + probability + optional scores) is also compatible: the module would pack that facade into one or more System One questions, as the citation-check cookbook already does in application code. Prefer keeping the three kinds in the slot if issue 10 wants one capability to cover route / score / gate without extra slots.

### What must **not** leak into playbooks

- Model ids (`jev-latest`, `jev-1.13.0`)
- Env vars (`TYPESAFE_API_KEY`)
- Vendor question type names if we adopt the generic `kind` aliases above
- "If Jev is installed…" — the test is "if `validation.judge` is registered"

### Practical constraints the registry ticket should know

- **Hosted only.** The module needs network + a key. No local fallback from TypeSafe.
- **Text state.** Diffs, traces, and test output must be serialized to text/JSON before the call.
- **No rationale string.** If a playbook wants "why," it must call a different capability or skip.
- **Pin the version** after tuning thresholds; aliases move. Log `provider_model`. ([Models](https://docs.typesafe.ai/models.md))
- **English-first.** Non-English judge payloads need their own eval.
- **Literal questions.** Write the actual criterion; Jev will not infer unstated intent. ([jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md))
- **Decompose.** One snap judgment per question; combine in code. A blob prompt "is this PR good?" is the anti-pattern TypeSafe documents. ([Primitives](https://docs.typesafe.ai/primitives.md))
- **Timeouts / 529.** Treat the judge as skippable: if the provider 529s or exceeds the client timeout, the capability should return a typed error the playbook can escalate, not hang the host.

---

## 8. Sources

Primary (used for claims):

- [docs.typesafe.ai/llms.txt](https://docs.typesafe.ai/llms.txt) — docs index
- [Introduction](https://docs.typesafe.ai/introduction.md)
- [Quick start](https://docs.typesafe.ai/introduction/quickstart.md)
- [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents.md)
- [System One](https://docs.typesafe.ai/concepts/system-one.md)
- [State](https://docs.typesafe.ai/concepts/state.md)
- [Primitives](https://docs.typesafe.ai/primitives.md), [Choice](https://docs.typesafe.ai/primitives/choice.md), [Noul](https://docs.typesafe.ai/primitives/noul.md)
- [Confidence](https://docs.typesafe.ai/confidence.md)
- [How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)
- [API reference](https://docs.typesafe.ai/api) / [api.md](https://docs.typesafe.ai/api.md)
- [Models](https://docs.typesafe.ai/models.md)
- [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- [Agent skill](https://docs.typesafe.ai/agent-skill.md)
- [Python SDK](https://docs.typesafe.ai/sdk/python.md), [constants](https://docs.typesafe.ai/sdk/python/api/constants.md), [usage](https://docs.typesafe.ai/sdk/python/usage.md)
- [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript.md), [TypeSafeClientConfig](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TypeSafeClientConfig.md)
- [Citation-check cookbook](https://docs.typesafe.ai/cookbooks/citation_check.md)
- [Guardrails cookbook](https://docs.typesafe.ai/cookbooks/llm_guardrails.md)
- [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [Homepage](https://typesafe.ai/)
- [github.com/typesafe-ai](https://github.com/typesafe-ai)
- [Official skill SKILL.md](https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md)
- [system-one-adapter-python](https://github.com/typesafe-ai/system-one-adapter-python)

This repo: `GLOSSARY.md`; map issue 1; registry issue 10.

Not used as evidence: LangSmith/Arize/community blogs, `jevtypesafeai.com` proxies, unofficial `jev-mcp` servers.
