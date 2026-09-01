# 🏛️ DM MONOLITH — Distributed Mesh Routing Plane

## Mission Statement

Build the **dm monolith**: a unified distributed mesh routing plane that eliminates CLI fragmentation, unifies config/memory/workflows, routes tasks across backends with quota-aware intelligence, and applies token-saving techniques from token_saver + primordial-mesh-titan. Antigravity is the abundant primary resource; Claude Code is preferred but quota-managed; free tiers absorb routine load.

---

## Chapter Architecture

| Chapter | Title | Skills Loaded | Output |
|---------|-------|---------------|--------|
| 1 | Mission Architecture & Epistemic Foundation | `epicenter`, `far-away-party`, `research-study-act` | MISSION.md, ROADMAP.md, CONTEXT.md, EVIDENCE.md, HANDOFF.md |
| 2 | Distributed Mesh & Backend Unification | `make-it-heavy`, `architecture`, `clean-code` | Unified 7-backend mesh (Antigravity + Claude Code + free tiers + Ollama + Novita) |
| 3 | Token Economy & Context Engineering | `token-saver`, `mega-token-saver`, `make-it-heavy` | Pure pointer externalization + semantic compression + context compaction |
| 4 | Always-On Governance & Verification | `apex-always-on-core`, `quality-gate`, `code-review-checklist` | Always-on cognitive foundation + verification gates |
| 5 | Config Substrate Unification | `architecture`, `clean-code`, `security-review` | apex-config.yaml + per-CLI overlays + generator script |
| 6 | Memory Plane Unification | `agent-memory-systems`, `omni-memory-core`, `quality-gate` | Memory gateway MCP (sqlite + files + Qdrant + Pinecone + mem0 + supermemory) |
| 7 | Workflow & Constitution Unification | `far-away-party`, `epicenter`, `roadmap-builder` | Workflow registry + constitution files |
| 8 | Integration, Testing & Deployment | `quality-gate`, `code-review-checklist`, `research-study-act` | Full dm monolith operational + L2 verified |

---

## CHAPTER 1: Mission Architecture & Epistemic Foundation

### Skills to Load
1. **`epicenter`** — L0/L1/L2 verification, the law of action, upgrade protocol
2. **`far-away-party`** — 5-file mission state contract, 8-step execution algorithm, compounding route matrix
3. **`research-study-act`** — Tri-phase mandate (Research → Study → Act)

### Objectives
- Establish the epistemic foundation: no claim without L2 verification
- Create the 5 durable state files as the absolute mission source of truth
- Map the compounding route matrix to the dm monolith build
- Define acceptance criteria for each chapter gate

### The 5 Durable State Files (far-away-party contract)

| State File | Purpose | Location |
|---|---|---|
| `MISSION.md` | Bounded intent, non-negotiable criteria, exclusions | `APEX_SYSTEM/INFRASTRUCTURE/apex-core/mission/` |
| `ROADMAP.md` | Phase gates, dependency order, chunk boundaries | same |
| `CONTEXT.md` | Lean operational capsule of current realities | same |
| `EVIDENCE.md` | Physical test results, compiler receipts, proof hashes | same |
| `HANDOFF.md` | Exact state, last verified gate, next actionable step | same |

### Compounding Route Matrix (applied to dm monolith)

| Mandatory Core | Conditional Route | When Activated |
|---|---|---|
| `long-horizon-core` | `capability-readiness` | Antigravity/Claude Code API access unverified |
| `long-horizon-core` | `signal-to-decision-loop` | Backend quota threshold triggers reroute |
| `long-horizon-core` | `guarded-automation` | Config generation / credential rotation |
| `long-horizon-core` | `evidence-to-evolution` | Token savings prove need for new compression |
| `long-horizon-core` | `recon-and-map` | CLI config drift detected |
| `long-horizon-core` | `skill-forge` | Recurring routing pattern spotted |
| `long-horizon-core` | `automation-control` | Backend health checks / quota monitoring |

### Verification Gate (Chapter 1 → 2)
- [ ] MISSION.md defines non-negotiable criteria for dm monolith
- [ ] ROADMAP.md has explicit validation criteria per chapter
- [ ] EVIDENCE.md contains L2 proof of current environment state
- [ ] HANDOFF.md enables lossless resumption
- [ ] All claims tagged with epistemic layer (L0/L1/L2)

---

## CHAPTER 2: Distributed Mesh & Backend Unification

### Skills to Load
1. **`make-it-heavy`** — Exhaustive rigor, multi-dimensional verification, zero placeholders
2. **`architecture`** — Structural decision-making, ADR documentation
3. **`clean-code`** — Pragmatic implementation standards

### Current State (Recon)

| Backend | Type | Status | Location |
|---|---|---|---|
| Ollama | Local | ✅ Running (2 models) | `~/.local/bin/ollama` |
| MeshLLM | Distributed GPU | ⚠️ localhost:9337 (unverified) | `backends.py` |
| TITAN | Local agent framework | ⚠️ localhost:48420 (unverified) | `backends.py` |
| Kilo | Cloud aggregator | ✅ Configured | `backends.py` |
| OpenRouter | Cloud aggregator | ✅ 25+ free models | `server.py` |
| Novita | Cloud failover | ✅ Configured | `backends.py` |
| **Antigravity** | **Google enterprise** | ❌ Not in mesh | `~/.config/antigravity/` |
| **Claude Code** | **Anthropic preferred** | ❌ Not installed | Not present |

### Objectives
1. Add **AntigravityBackend** to the mesh — Google enterprise tier, the abundant primary
2. Add **ClaudeCodeBackend** to the mesh — preferred but quota-managed
3. Implement quota-aware routing: free tiers → Antigravity → Ollama → Claude Code → Novita
4. Verify each backend with L2 health checks (not just "configured")
5. Document the mesh topology in an ADR

### Backend Priority Order (quota-aware)

```
1. openrouter_free  — zero cost, 25+ models (Nemotron, Inkling, MiniMax, etc.)
2. antigravity     — Google enterprise, abundant, high ceiling
3. ollama           — local, unlimited, hardware-bound
4. mesh-llm         — distributed GPU mesh (if healthy)
5. titan            — local agent framework (if healthy)
6. claude_code      — preferred, quota-managed, only when required
7. novita           — paid failover of last resort
```

### Token-Saver Integration Points
- Pure pointer externalization (from token_saver/pure_pointer.py): large context → SHA-256 pointers
- Semantic compression (from token_saver/semantic_compressor.py): TF-IDF line scoring
- Consistent hashing ring (from token_saver/mesh.py): distributed cache routing
- UDP peer discovery (from token_saver/discovery.py): backend auto-discovery

### Verification Gate (Chapter 2 → 3)
- [ ] All 7 backends respond to health checks (L2: actual API call, not config check)
- [ ] Quota-aware routing logic implemented and unit-tested
- [ ] Antigravity backend dispatches to Google enterprise tier
- [ ] Claude Code backend dispatches with quota guard
- [ ] Fallback chain verified: if backend N fails, N+1 takes over
- [ ] ADR documented: why this topology, why this priority order

---

## CHAPTER 3: Token Economy & Context Engineering

### Skills to Load
1. **`token-saver`** — Compaction, prompt packs, handoff files, budget tracking
2. **`mega-token-saver`** — Same (bundled catalog version)
3. **`make-it-heavy`** — Exhaustive rigor for routing logic

### Techniques to Integrate (from repos)

| Technique | Source | What it does | Token savings |
|---|---|---|---|
| **Pure Pointer Externalization** | `token_saver/src/pure_pointer.py` | Large content → SHA-256 file + compact pointer `[ptr:sha256://...|n=...]` | 60-90% for large context |
| **Semantic Compression** | `token_saver/src/semantic_compressor.py` | TF-IDF + positional + structural scoring, keeps top-N lines | 40-70% for verbose text |
| **Consistent Hashing Ring** | `token_saver/server/mesh.py` | HashRing with virtual nodes, distributed cache routing | Eliminates duplicate context |
| **EliteMemoryCache** | `token_saver/token_saver_elite_core.py` | JSON persistence, atomic writes, TTL, honest metrics | Avoids re-fetching |
| **EliteTokenBridge** | `token_saver/token_saver_elite_core.py` | Deterministic request optimizer, batching, compression | Deduplicates requests |
| **UDP Peer Discovery** | `token_saver/server/discovery.py` | UDP broadcast/listener, PeerRegistry | Auto-discovers cache peers |
| **Distributed Context Layer** | `PRIMORDIAL-MESH-TITAN/context.py` | Supabase (vectors) + Neo4j (relationships) + Vercel KV (session) | Context offload to graph |

### Objectives
1. Integrate pure pointer externalization into the dm monolith's context pipeline
2. Integrate semantic compression for verbose outputs (logs, transcripts)
3. Build the distributed context layer (Supabase + Neo4j + Vercel KV)
4. Wire EliteMemoryCache as the request dedup layer
5. Measure and verify token savings (before/after byte counts)

### Token Budget Architecture

```
Session Budget: 100K tokens (example)
├── System prompt: 5K (condensed constitution)
├── Context capsule: 10K (CONTEXT.md, not full history)
├── Working memory: 60K (active task)
│   ├── Pure pointers: 2K (resolves to 50K+ content on demand)
│   ├── Compressed context: 8K (from 20K original)
│   └── Active content: 50K
├── Reserve: 15K (overflow / fallback)
└── Compaction threshold: 70% (auto-compact at 70K)
```

### Verification Gate (Chapter 3 → 4)
- [ ] Pure pointer externalization: 10K+ character context reduced to <500 char pointers
- [ ] Semantic compression: verbose text reduced 50%+ with saliency preserved
- [ ] Distributed context: chunks stored in Supabase, relationships in Neo4j
- [ ] Cache hit rate >60% for repeated queries (L2: actual metrics)
- [ ] Token savings measured and logged (before/after byte counts in EVIDENCE.md)

---

## CHAPTER 4: Always-On Governance & Verification

### Skills to Load
1. **`apex-always-on-core`** — Continuous cognitive foundation, cognitive firewall
2. **`quality-gate`** — Phase boundary verification, evidence-backed decisions
3. **`code-review-checklist`** — Before declaring done

### Objectives
1. Establish the always-on cognitive foundation (read-only by default)
2. Define the cognitive firewall: what the dm monolith can/cannot do autonomously
3. Implement human control points for irreversible actions
4. Build verification gates at every chapter boundary
5. Ensure 100% test assertions and receipts verify

### Cognitive Firewall (from apex-always-on-core)

| Mode | Allowed Actions | Forbidden Actions |
|---|---|---|
| `read_only` (default) | read_repository, run_local_tests, write_run_artifacts, emit_receipt | external_mutation, network_send, file_submission, deletion, deployment, merge, credential_access, legal_filing |
| `execute` (elevated) | + backend_dispatch, config_generation, cache_wipe | + external_mutation still forbidden without human approval |

### Human Control Points
- `approve_production_release` — required before pushing to origin/main
- `escalate_critical_anomalies` — required on backend health failure
- `approve_quota_burn` — required before Claude Code dispatch above threshold
- `approve_credential_rotation` — required before key rotation

### Verification Gates (every chapter boundary)
1. Read acceptance criteria from ROADMAP.md
2. Execute promised tests (not creator's claim)
3. Check completeness, correctness, consistency, traceability
4. Record pass/fail/conditional-pass in EVIDENCE.md
5. On failure: classify cause, return to owner, prohibit advancement

### Verification Gate (Chapter 4 → 5)
- [ ] Cognitive firewall implemented and tested
- [ ] Human control points wired to dm monolith
- [ ] All chapter 1-3 gates passed with evidence
- [ ] 100% test assertions green (L2: actual test run, not claim)

---

## CHAPTER 5: Config Substrate Unification

### Skills to Load
1. **`architecture`** — Structural decision-making for config topology
2. **`clean-code`** — Implementation standards for generator
3. **`security-review`** — Credential handling, secret rotation

### Objectives
1. Build `apex-config.yaml` — the canonical shared substrate
2. Build `generate-cli-configs.py` — YAML + overlays → CLI configs
3. Create per-CLI overlays (lean: model + enabled MCPs + UI prefs)
4. Eliminate hardcoded secrets (OpenCode currently has hardcoded key)
5. Unify MCP server definitions (25 servers × 3 CLIs → 25 definitions, 3 enablement lists)

### Config Topology

```
apex-config.yaml (canonical)
├── credentials (API keys, tokens, URLs)
├── mcp_servers (25 servers, commands, env)
├── model_providers (7 providers, base URLs)
├── agent_personas (28 personas, prompts, models)
├── workflows (16+ named operations)
├── constitution (full + condensed)
├── memory_gateway (routing rules, backends)
└── skills_paths (4 directories)

Overlays (lean per-CLI):
├── overlays/kilo.json → model + mcp_enablement + ui
├── overlays/opencode.json → model + mcp_enablement + ui
└── overlays/antigravity.json → model + mcp_enablement + ui

Generator:
scripts/generate-cli-configs.py
├── reads apex-config.yaml
├── reads overlay per CLI
├── merges (overlay wins on conflicts)
├── writes kilo.json, opencode/config.json, antigravity/models_config.json
└── validates: no hardcoded secrets, all refs resolve
```

### Security Requirements (security-review)
- Zero hardcoded secrets in any generated config
- All credentials referenced via `${ENV_VAR}` or vault path
- `.env` file permissions: `0o600`
- Config generation is deterministic (same input → same output)
- Generated configs are git-ignored (only overlays + YAML are committed)

### Verification Gate (Chapter 5 → 6)
- [ ] apex-config.yaml contains all 25 MCP servers, 7 providers, 28 personas
- [ ] Generator produces valid configs for all 3 CLIs
- [ ] Zero hardcoded secrets in generated configs (L2: grep verification)
- [ ] Overlay diffs are minimal (model + enablement + UI only)
- [ ] Idempotent: running generator twice produces identical output

---

## CHAPTER 6: Memory Plane Unification

### Skills to Load
1. **`agent-memory-systems`** — Memory tier choice, retrieval strategy
2. **`omni-memory-core`** — 291k-file cross-cloud vector indexing, Hebbian weights
3. **`quality-gate`** — Phase boundary verification

### Current Fragmentation

| Backend | Type | Kilo | OpenCode | Antigravity |
|---|---|---|---|---|
| unified-memory MCP | Local file | ✅ | ✅ | ❌ |
| memory MCP | In-memory | ❌ | ✅ | ❌ |
| supermemory | Cloud API | ❌ | ✅ | ❌ |
| mem0 | Cloud API | ❌ | ✅ | ❌ |
| sqlite | Local DB | ❌ | ✅ | ❌ |
| Qdrant | Vector cloud | ❌ | ✅ | ❌ |
| Pinecone | Vector cloud | ❌ | ❌ | ❌ |
| omni-memory-core | 291k index | Skill | Skill | ❌ |

### Objectives
1. Build memory-gateway MCP — single access point for all memory backends
2. Implement routing: short-term (context) → long-term local (sqlite/files) → long-term cloud (vectors)
3. Implement dedup: don't store same fact in mem0 AND supermemory AND Qdrant
4. Wire omni-memory-core (291k index) as the vector backend
5. All CLIs talk to memory-gateway, not to individual backends

### Memory Gateway Architecture

```
Memory Gateway MCP (one server)
├── short-term: context window (per-session)
├── long-term local: sqlite (kilo_orchestration.db) + files (pure pointers)
└── long-term cloud: Qdrant (vectors) + Pinecone (production) + mem0 + supermemory

Routing rules:
- Query → check short-term → check local → check cloud (parallel)
- Write → short-term always + local always + cloud (async, by policy)
- Dedup → SHA-256 content hash → skip if already stored
- Retrieval → merge results from all backends → rank by relevance → return top-K
```

### Verification Gate (Chapter 6 → 7)
- [ ] Memory gateway responds to store/retrieve/list operations
- [ ] Dedup verified: same content stored once across backends
- [ ] Retrieval merges results from 3+ backends
- [ ] All CLIs can access memory via gateway (not direct backend)
- [ ] L2: actual store→retrieve→verify cycle with SHA-256 check

---

## CHAPTER 7: Workflow & Constitution Unification

### Skills to Load
1. **`far-away-party`** — Mission governance, workflow patterns
2. **`epicenter`** — Epistemic core, L0/L1/L2 verification
3. **`roadmap-builder`** — Dependency-aware work chunking

### Objectives
1. Build the workflow registry — 16+ named operations, CLI-native triggers
2. Define the constitution — full (AGENTS.md) + condensed (instructions.md)
3. Unify agent personas — 28 personas in shared library, all CLIs dispatch
4. Wire workflow triggers: OpenCode `/commands`, Kilo skills, Antigravity aliases

### Workflow Registry (from OpenCode commands)

| Workflow | Agent | Template | CLI Trigger |
|---|---|---|---|
| swarm | reasoner→synthesizer→auditor→perception | apex_swarm_dialectic.py | /swarm, skill, alias |
| repair | auditor + synthesizer | apex_repair_loop.py | /repair, skill, alias |
| harmonize | fleet-git-harmonizer | apex_repo_harmonizer.py | /harmonize, skill, alias |
| forensics | forensics | apex_epistemic_chunker.py | /forensics, skill, alias |
| bates | forensics | apex_bates_stamper.py | /bates, skill, alias |
| omni-ml | data | apex_omni_cloud_ml.py | /omni, skill, alias |
| legal-search | legal | apex-legal-search | /legal-search, skill, alias |
| polyglot | polyglot | apex_polyglot | /polyglot, skill, alias |

### Constitution Structure

```
constitution/
├── AGENTS.md (full, 300+ lines — the doctrine)
├── instructions.md (condensed, 8 lines — system prompt)
└── epistemic-ladder.md (L0-L6 — from epicenter)

All CLIs reference the same files:
→ OpenCode: instructions: [condensed]
→ Kilo: system_prompt: full (or condensed)
→ Antigravity: system_message: condensed
```

### Verification Gate (Chapter 7 → 8)
- [ ] Workflow registry contains 16+ operations with agent bindings
- [ ] Each workflow dispatchable from all 3 CLIs
- [ ] Constitution files generated and referenced by all CLIs
- [ ] Agent personas shared (28 personas, no per-CLI duplication)
- [ ] L2: dispatch a workflow from each CLI, verify correct agent + model

---

## CHAPTER 8: Integration, Testing & Deployment

### Skills to Load
1. **`quality-gate`** — Final verification, evidence-backed acceptance
2. **`code-review-checklist`** — Final self-audit
3. **`research-study-act`** — Tri-phase: Research (verify), Study (audit), Act (deploy)

### Objectives
1. End-to-end integration test: task in → dm monolith routes → backend executes → result out
2. Verify quota-aware routing: free tiers preferred, Claude Code quota-guarded
3. Verify token savings: pure pointers + semantic compression active
4. Verify memory unification: all CLIs see same memory plane
5. Verify config unification: generator produces consistent configs
6. Full regression: all previous chapter gates still pass
7. Deploy: wire dm monolith as the single MCP that all CLIs talk to

### Integration Test Matrix

| Test | Input | Expected | Verification |
|---|---|---|---|
| Route to free tier | Simple query | Dispatches to OpenRouter free | L2: check backend field in response |
| Route to Antigravity | Complex reasoning | Dispatches to Google enterprise | L2: check backend field |
| Route to Claude Code | Claude-only task | Dispatches with quota guard | L2: check quota check logged |
| Fallback chain | OpenRouter 429 | Falls back to Novita | L2: check fallback logged |
| Pure pointer | 10K context | Returns <500 char pointer | L2: byte count verification |
| Semantic compression | Verbose log | Returns 50% lines, saliency preserved | L2: line count + TF-IDF check |
| Memory dedup | Store same fact twice | Stored once, dedup logged | L2: backend query shows 1 entry |
| Config consistency | Run generator twice | Identical output | L2: diff = empty |
| Workflow dispatch | /swarm from Kilo | Correct agent chain executes | L2: receipt in EVIDENCE.md |

### Deployment Checklist
- [ ] dm monolith MCP server running and healthy
- [ ] All 3 CLIs configured to use dm monolith (not direct backends)
- [ ] Quota monitoring active (Claude Code burn rate tracked)
- [ ] Token savings metrics flowing to EVIDENCE.md
- [ ] Memory gateway serving all CLIs
- [ ] Config generator idempotent and committed
- [ ] All chapter gates passed with evidence
- [ ] HANDOFF.md updated with exact deployment state

### Final Verification
- [ ] 100% test assertions green
- [ ] Zero hardcoded secrets in any config
- [ ] All claims in EVIDENCE.md backed by L2 proof
- [ ] Non-creator can reproduce every gate decision from named criteria

---

## Appendix A: Skill Load Summary

| Chapter | Primary Skills | Supporting |
|---|---|---|
| 1 | epicenter, far-away-party, research-study-act | — |
| 2 | make-it-heavy, architecture, clean-code | — |
| 3 | token-saver, mega-token-saver, make-it-heavy | clean-code |
| 4 | apex-always-on-core, quality-gate, code-review-checklist | — |
| 5 | architecture, clean-code, security-review | — |
| 6 | agent-memory-systems, omni-memory-core, quality-gate | — |
| 7 | far-away-party, epicenter, roadmap-builder | — |
| 8 | quality-gate, code-review-checklist, research-study-act | — |

## Appendix B: Repo Technique Extraction

| Repo | Technique | Chapter | Status |
|---|---|---|---|
| token_saver/src/pure_pointer.py | Content-addressed payload offload | 3 | Extract to dm monolith |
| token_saver/src/semantic_compressor.py | TF-IDF line scoring compression | 3 | Extract to dm monolith |
| token_saver/server/mesh.py | Consistent hashing ring (HashRing) | 3 | Extract to dm monolith |
| token_saver/server/discovery.py | UDP peer discovery | 3 | Extract to dm monolith |
| token_saver/token_saver_elite_core.py | EliteMemoryCache + EliteTokenBridge | 3 | Extract to dm monolith |
| PRIMORDIAL-MESH-TITAN/context.py | Distributed context (Supabase+Neo4j+KV) | 3, 6 | Extract to dm monolith |
| PRIMORDIAL-MESH-TITAN/mesh-config.json | Free-tier mesh topology (10+ providers) | 2 | Reference architecture |
| openrouter-free-gateway/server.py | MCP server + free model routing | 2 | Extend with new backends |
| openrouter-free-gateway/backends.py | BackendManager + 6 backends | 2 | Extend to 7+ backends |

## Appendix C: Non-Goals

- Not building a new LLM from scratch (the PyTorch model in PMT is a toy — ignore it)
- Not replacing Antigravity's native capabilities — only routing to them
- Not storing PII in any memory backend (apex_scrubber.py gate)
- Not autonomous legal filing (human control point required)
- Not unbounded external state mutations (cognitive firewall)

---

*This document is the ROADMAP.md for the dm monolith mission. It lives at*
`APEX_SYSTEM/INFRASTRUCTURE/apex-core/mission/ROADMAP.md`
*Execution begins with Chapter 1 when authorized.*
