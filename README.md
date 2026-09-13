# APEX Core Infrastructure

`GlacierEQ/apex-core` is a core infrastructure repository for APEX automation and orchestration mechanisms. It owns the implementation and contracts that actually live in this repository; it does **not** constitute a universal source of truth, identity root, or sovereign control plane for the entire GlacierEQ estate.

The estate is polycentric/holographic. Repositories, runtimes, memory systems, databases, evidence stores, deployments, control surfaces, and current Operator direction remain provenance-bound peers with scoped authority. `apex-core` coordinates and implements infrastructure where it owns that responsibility; it does not erase or subordinate peer systems merely because they participate in APEX.

## Contents
* `scripts/apex_surgical_engine.sh`: The 4-step autonomous branch synchronization and AST harvesting engine.
* `scripts/apex_ai_synthesis.py`: The AI compiler that dynamically translates aborted git patches into executable Markdown prompts for autonomous agent resolution.

## Authority Boundary
- Current Operator direction controls mission and operation class.
- This repository controls the code and contracts it actually owns.
- External factual state is controlled by the relevant source-bearing systems.
- Verification/readback controls whether execution is complete.
- Cross-repository relationships preserve provenance and do not imply global hierarchy.

*Governance supports function; it does not replace execution. Authority remains scoped to responsibility.*

### Machine–Mesh Protocol Manifest

<!-- glacier-eq-protocol:start -->
```yaml
{
  "schema": "glacier-eq.readme.machine-mesh/v1",
  "repository": {
    "id": "GlacierEQ/apex-core",
    "url": "https://github.com/GlacierEQ/apex-core",
    "readme_contract": "estate-machine-v1",
    "default_branch": "main"
  },
  "machine": {
    "repository_kind": "migration-residue",
    "public_api": "inspect-declared-entrypoints",
    "protocol_files": [],
    "entrypoints": [
      {
        "kind": "script-area",
        "path": "scripts",
        "policy": "inspect-before-use"
      },
      {
        "kind": "test-area",
        "path": "tests",
        "policy": "run-before-reliance"
      },
      {
        "kind": "documentation-area",
        "path": "docs",
        "policy": "read-as-context"
      }
    ]
  },
  "presentation": {
    "architecture": [
      "recruiter",
      "master",
      "machine",
      "mesh"
    ],
    "authority": {
      "capability": "stone-psysoc-x",
      "repository": "GlacierEQ/AKOS",
      "manifest": "stones/psysoc-x/stone.json",
      "engine": "infinity_stones/psysoc_x.py"
    },
    "truth_invariant": "presentation-may-change-sequence-density-tone-and-style; facts-evidence-uncertainty-provenance-dignity-and-reader-agency-may-not"
  },
  "license": {
    "class": "NO_ROOT_LICENSE_DETECTED",
    "status": "ORIGINALITY_AND_PROVENANCE_REVIEW_REQUIRED",
    "controlling_path": null,
    "policy": "GlacierEQ/job-app-helix/LICENSE_POLICY.json",
    "may_relicense_automatically": false,
    "upstream_rights_must_be_preserved": false
  },
  "mesh": {
    "primary_home": null,
    "branch": "migration-residue",
    "subcategory": "unresolved-primary-home",
    "routing": [
      {
        "relation": "estate-map",
        "target": "GlacierEQ/monolith",
        "url": "https://github.com/GlacierEQ/monolith"
      }
    ],
    "boundaries": [
      "routing-does-not-transfer-source-code-evidence-deployment-or-lifecycle-authority",
      "generated-contract-is-a-source-index-not-a-runtime-or-provider-receipt",
      "implementation-and-provider-state-require-independent-evidence",
      "presentation-calibration-cannot-promote-claim-or-evidence-state",
      "license-automation-cannot-relicense-unresolved-upstream-or-third-party-rights"
    ]
  },
  "provenance": {
    "generated_by": "GlacierEQ/job-app-helix",
    "generator_contract": "estate-machine-v1",
    "classification_source": null,
    "classification_evidence_path": null,
    "classification_evidence_blob_sha": null,
    "classification_status": null,
    "contract_digest": "92c858469a769fa02f8e942e96cb45c70fdb206154662ad115ec19346467a517"
  }
}
```
<!-- glacier-eq-protocol:end -->
