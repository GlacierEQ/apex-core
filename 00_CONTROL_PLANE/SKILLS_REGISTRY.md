# APEX SKILLS TOPOLOGY REGISTRY
> Auto-generated: 2026-09-03 | 171 SKILL.md files | 3 locations | 74 unique names

---

## I. INVENTORY SUMMARY

| Source | Location | Count | Role |
|---|---|---|---|
| **Grok Top-Level** | `~/.grok/skills/` | 59 | Core APEX skills, pillars, infrastructure |
| **Grok World** | `~/.grok/skills/world/` | 32 | External symlinks (Anthropic, Vercel, ToB, Pocock) |
| **Grok Mimo** | `~/.grok/skills/mimo_skills/` | 22 + 43 nested = 65 | MimoCode workflows (sales, data, design, etc.) |
| **Gemini Apex** | `~/.gemini/skills/apex-arsenal/` | 15 | Gemini-specific APEX arsenal |
| **GRAND TOTAL** | | **171** | |

---

## II. EXACT DUPLICATES (Same name, multiple locations)

| Skill | Grok | Gemini | Verdict |
|---|---|---|---|
| `epicenter` | 1,803B | 1,801B | **MERGE** — near-identical, keep gemini (newer) |
| `make-it-heavy` | 1,649B | 3,214B | **KEEP gemini** — 2x richer, grok is thin stub |
| `mega-web` | 2,632B | 2,632B | **MERGE** — exact same size, pick one |

---

## III. FUNCTIONAL OVERLAP GROUPS

### Group 1: MEMORY (4 skills → recommend 2)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `memory-connect` | grok | 4,759B | **MERGE into memory-unified** |
| `memory-unified` | grok | 6,124B | **KEEP** — most comprehensive |
| `unified-memory-connect` | grok | 4,819B | **MERGE into memory-unified** |
| `memory-pillar` | grok | 595B | **RETIRE** — thin router, unnecessary |

### Group 2: SWARM (3 skills → recommend 1)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `swarm-orchestrator` | grok | 8,992B | **KEEP** — the real engine |
| `swarm-pillar` | grok | 727B | **RETIRE** — thin router |
| `apex-orchestration` | grok | 5,815B | **MERGE into swarm-orchestrator** |

### Group 3: EPISTEMIC (2 skills → recommend 1)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `epicenter` | grok+gemini | ~1,800B | **KEEP** — core doctrine |
| `epistemic-gate` | grok | 2,075B | **MERGE into epicenter** |

### Group 4: TOKEN OPTIMIZATION (4 skills → recommend 2)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `make-it-heavy` | gemini | 3,214B | **KEEP** — primary execution mode |
| `hyper-efficiency-flow` | grok | 3,575B | **KEEP** — complementary, distinct approach |
| `token-saver` | grok | 4,877B | **MERGE into hyper-efficiency-flow** |
| `max-token-saver` | gemini | 2,739B | **MERGE into hyper-efficiency-flow** |

### Group 5: GENIUS (4 skills → recommend 2)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `genius-mastery` | grok | 2,709B | **KEEP** — core kernel |
| `genius-entity-forge` | grok | 2,315B | **KEEP** — entity creation |
| `genius-epistemic-engineering` | grok | 3,296B | **MERGE into genius-mastery** |
| `apex-genius-mastery` | grok | 2,049B | **RETIRE** — adapter, no unique value |

### Group 6: VERIFICATION (2 skills → recommend 1)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `verification` | grok | 7,930B | **KEEP** — comprehensive |
| `verification-before-completion` | grok | 4,203B | **MERGE into verification** |

### Group 7: MEGA WEB (2 skills → recommend 1)
| Skill | Location | Size | Verdict |
|---|---|---|---|
| `mega-web` | grok+gemini | 2,632B | **KEEP** — ceiling web engineering |
| `apex-universal-mcp-powerhouse` | gemini | 2,001B | **RETIRE** — MCP focus, not web |

### Group 8: PILLAR ROUTERS (15 skills → recommend 5-8)
| Pillar | Size | Verdict |
|---|---|---|
| `boot-pillar` | 780B | **KEEP** — session init |
| `data-pillar` | 592B | **RETIRE** — data-analytics covers this |
| `design-pillar` | 812B | **RETIRE** — product-design covers this |
| `documents-pillar` | 677B | **RETIRE** — docx/pdf/pptx/xlsx cover this |
| `forensic-pillar` | 655B | **KEEP** — unique domain |
| `game-pillar` | 652B | **RETIRE** — thin, no real engine |
| `helix-pillar` | 868B | **RETIRE** — helix-pro-code covers this |
| `infra-pillar` | 638B | **RETIRE** — bootstrap covers this |
| `intelligence-pillar` | 656B | **RETIRE** — deep-research covers this |
| `law-pillar` | 730B | **KEEP** — unique domain |
| `memory-pillar` | 595B | **RETIRE** — memory-unified covers this |
| `sales-pillar` | 619B | **RETIRE** — sales skill covers this |
| `security-pillar` | 842B | **KEEP** — unique domain |
| `swarm-pillar` | 727B | **RETIRE** — swarm-orchestrator covers this |
| `apex-pillars` | 2,721B | **RETIRE** — meta-router, adds no value |

---

## IV. BROKEN RISK: WORLD SYMLINKS

All 32 world skills are symlinks to `~/.grok/plane/skill-cache/`. If the cache is cleared or the plane is reset, **all 32 skills vanish**. Recommendation: copy critical ones to `~/.grok/skills/world/` as real files.

---

## V. HIDDEN SKILLS: MIMO NESTED WORKFLOWS

43 nested workflow skills exist under `mimo_skills/*/workflows/` but are **NOT exposed in the system prompt's `available_skills`**. They load only when the parent skill is invoked. Key hidden skills:

### Sales (20 hidden workflows)
`analyze-account-signals`, `apollo`, `build-business-case`, `build-competitive-brief`, `enrich-company-and-contact-data`, `find-customer-quotes`, `find-key-internal-sources`, `follow-up-after-call`, `get-rep-call-feedback`, `hubspot`, `index`, `plan-deal-strategy`, `prepare-for-meeting`, `prioritize-accounts`, `review-forecast`, `review-rep-call-trends`, `sales-company-research`, `salesforce`, `zoominfo`, `answers-ask-user-input`

### Data Analytics (14 hidden workflows)
`analyze-data-quality`, `build-dashboard`, `build-report`, `create-data-context`, `design-kpis`, `gather-business-context`, `index`, `jupyter-notebooks`, `kpi-reporting`, `market-sizing`, `metric-diagnostics`, `product-business-analysis`, `validate-data`, `visualize-data`

### Product Design (9 hidden workflows)
`audit`, `design-qa`, `get-context`, `ideate`, `image-to-code`, `index`, `share`, `url-to-code`, `user-context`

---

## VI. PHANTOM SKILLS (In System Prompt, No File)

3 skills are listed in the system prompt `available_skills` but **have no SKILL.md file anywhere on disk**:

| Skill | Status |
|---|---|
| `report-to-google-doc` | **NEVER CREATED** — referenced but not implemented |
| `report-to-google-slides` | **NEVER CREATED** — referenced but not implemented |
| `report-to-pdf` | **NEVER CREATED** — referenced but not implemented |

These are phantom references. Either create them or remove from prompt.

Additionally, 37 skills listed in the system prompt are actually **nested mimo workflows** (sales → `analyze-account-signals`, data-analytics → `build-report`, product-design → `audit`, etc.). They load indirectly through their parent skill, not as standalone entries.

---

## VII. OPTIMIZED TOPOLOGY (Target State)

### Keep (39 skills)
| Skill | Location | Role |
|---|---|---|
| `epicenter` | grok | Core epistemic doctrine |
| `make-it-heavy` | gemini | Primary execution mode |
| `mega-web` | grok | Ceiling web engineering |
| `swarm-orchestrator` | grok | Multi-agent engine |
| `genius-mastery` | grok | Genius kernel |
| `genius-entity-forge` | grok | Entity creation |
| `memory-unified` | grok | Memory infrastructure |
| `hyper-efficiency-flow` | grok | Token optimization |
| `verification` | grok | Full-story verification |
| `bootstrap` | grok | Project bootstrapping |
| `path-of-highest-power` | grok | Strategic escalation |
| `blueprint-long-run` | grok | Long-horizon execution |
| `context-capsule` | grok | Handoff compaction |
| `evidence-register` | grok | Source tracking |
| `handoff-record` | grok | Recovery points |
| `mission-contract` | grok | Bounded tasks |
| `quality-gate` | grok | Phase verification |
| `roadmap-builder` | grok | Dependency sequencing |
| `work-packet` | grok | Delegation units |
| `legal-automation-suite` | grok | Legal warfare |
| `digital-law-library-master` | grok | Law library |
| `library-of-links` | grok | Repository mesh |
| `repo-indexer` | grok | Codebase indexing |
| `sequential-thinking` | grok | Reasoning framework |
| `sovereign-operator` | grok | Sovereign protocol |
| `helix-pro-code` | grok | Pro-code engineering |
| `toolbelt` | grok | Tool map |
| `grok-capability-plane` | grok | Environment restore |
| `apex-aspen-grove-bootup` | gemini | Session init |
| `aspen-grove-core` | gemini | Quantum memory |
| `aspen-grove-router-integration` | gemini | MCP routing |
| `distributed-processing` | gemini | Delegation layer |
| `glaciereq-nervous-system` | gemini | Mission composition |
| `power-skill` | gemini | Max force ops |
| `prompt-optimizer` | gemini | Prompt refinement |
| `skill-connector-router` | gemini | Dynamic routing |
| `sovereign-connectors-exposer` | gemini | Connector orchestration |
| `apex-meta-skill-kernel` | gemini | Topology governance |
| `operator-is-the-universe` | grok | Ring -3 universal |

### Retire (20 skills)
`apex-always-on-core`, `apex-genius-mastery`, `apex-orchestration`, `apex-pillars`, `arrangement-core`, `data-pillar`, `design-pillar`, `documents-pillar`, `game-pillar`, `genius-epistemic-engineering`, `helix-pillar`, `infra-pillar`, `intelligence-pillar`, `memory-pillar`, `sales-pillar`, `swarm-pillar`, `token-saver`, `max-token-saver`, `unified-memory-connect`, `memory-connect`

### Merge (8 skills → into 4)
| Source | → Target |
|---|---|
| `epistemic-gate` | → `epicenter` |
| `apex-orchestration` | → `swarm-orchestrator` |
| `memory-connect` | → `memory-unified` |
| `unified-memory-connect` | → `memory-unified` |
| `token-saver` | → `hyper-efficiency-flow` |
| `max-token-saver` | → `hyper-efficiency-flow` |
| `genius-epistemic-engineering` | → `genius-mastery` |
| `verification-before-completion` | → `verification` |

### Mimo Skills: KEEP ALL (65)
These are production workflow skills with deep domain logic. No retirement needed.

### World Skills: KEEP ALL (32)
External community skills. No retirement needed, but **harden symlinks**.

---

## VIII. ACTIONS REQUIRED

1. **RETIRE** 20 thin router/stub skills (move to `~/.grok/skills/_retired/`)
2. **MERGE** 8 overlapping skills into their targets
3. **HARDEN** 32 world symlinks (copy critical ones as real files)
4. **EXPOSE** 43 hidden mimo nested workflows in system prompt
5. **DEDUP** 3 exact duplicates (epicenter, make-it-heavy, mega-web)

**Projected result: 171 → ~100 active skills, zero stubs, zero thin routers, all domain logic preserved.**
