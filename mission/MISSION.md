# 🏛️ DM MONOLITH — Mission Definition

## Bounded Intent

Build the **dm monolith**: a unified distributed mesh routing plane that eliminates CLI fragmentation across Kilo, OpenCode, and Antigravity. The dm monolith is the single routing layer that all CLIs talk to — unifying config, memory, workflows, and backend dispatch with quota-aware intelligence and token-saving techniques extracted from `token_saver` and `PRIMORDIAL-MESH-TITAN`.

## Non-Negotiable Criteria

1. **Antigravity is primary** — Google enterprise tier is the most abundant resource; it absorbs the majority of routed tasks
2. **Claude Code is preferred but quota-managed** — only dispatched when task requires Claude-specific capabilities AND free tiers cannot handle it
3. **Free tiers absorb routine load** — OpenRouter free models, Ollama local, absorb 80%+ of workload
4. **Zero hardcoded secrets** — all credentials via `${ENV_VAR}` or vault path, never in generated configs
5. **Zero CLI duplication** — MCP servers, personas, workflows defined once, referenced everywhere
6. **L2 verification for all claims** — no "done" without actual test execution receipts
7. **Token savings measured** — pure pointer externalization + semantic compression with before/after byte counts
8. **Cognitive firewall** — read-only by default, human control points for irreversible actions
9. **Lossless resumption** — HANDOFF.md enables instant continuation across any turn boundary

## Explicit Exclusions

- NOT building a new LLM (the PyTorch model in PMT is a toy — ignore it)
- NOT replacing Antigravity's native capabilities — only routing to them
- NOT storing PII in any memory backend (apex_scrubber.py gate applies)
- NOT autonomous legal filing (human control point required)
- NOT unbounded external state mutations (cognitive firewall enforced)
- NOT a single monolithic binary — the "monolith" is the unified routing plane, distributed by design

## Success Definition

The dm monolith is complete when:
- A task entered via ANY CLI (Kilo, OpenCode, Antigravity) is routed to the optimal backend
- Token savings are measurable and logged (>50% reduction on large context)
- All CLIs share one memory plane, one config substrate, one workflow registry
- Claude Code quota burn is near-zero for routine tasks
- A non-creator can reproduce every gate decision from named criteria in EVIDENCE.md

## Epistemic Foundation

All claims in this mission are tagged with their epistemic layer:
- **L0** (Presence): "I see X exists" — observation only
- **L1** (Structure): "X contains Y" — hypothesis, requires verification
- **L2** (Behavior): "I ran it; Z happened" — act and state as fact

No destructive act without timestamped backup. No claim without layer tag.
