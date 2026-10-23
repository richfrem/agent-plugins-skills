# Resource index

Owned resources for managing-rlm-cache. Run commands from the skill root, with the consumer
project selected separately. These are links to canonical files, not copies.

## Contents

- [References](#references)
- [Scripts and verification](#scripts-and-verification)
- [Executable assets and templates](#executable-assets-and-templates)
- [Dependencies](#dependencies)

## References

- [references/BLUEPRINT.md](BLUEPRINT.md)
- [references/RLM_ARCHITECTURE.md](RLM_ARCHITECTURE.md)
- [references/acceptance-criteria.md](acceptance-criteria.md)
- [references/cheapest_models.json](cheapest_models.json)
- [references/cheapest_models.md](cheapest_models.md)
- [references/diagrams/distillation_process.mmd](diagrams/distillation_process.mmd)
- [references/diagrams/logic.mmd](diagrams/logic.mmd)
- [references/diagrams/rlm-factory-architecture.mmd](diagrams/rlm-factory-architecture.mmd)
- [references/diagrams/rlm-factory-dual-path.mmd](diagrams/rlm-factory-dual-path.mmd)
- [references/diagrams/rlm-factory-workflow.mmd](diagrams/rlm-factory-workflow.mmd)
- [references/diagrams/rlm_late_binding_flow.mmd](diagrams/rlm_late_binding_flow.mmd)
- [references/diagrams/rlm_mechanism_workflow.mmd](diagrams/rlm_mechanism_workflow.mmd)
- [references/diagrams/rlm_tool_enrichment_flow.mmd](diagrams/rlm_tool_enrichment_flow.mmd)
- [references/diagrams/search_process.mmd](diagrams/search_process.mmd)
- [references/diagrams/unpacking.mmd](diagrams/unpacking.mmd)
- [references/diagrams/workflow.mmd](diagrams/workflow.mmd)
- [references/gap_analysis_rlm_v1.md](gap_analysis_rlm_v1.md)
- [references/interactive-setup.md](interactive-setup.md)
- [references/logic.mmd](logic.mmd)
- [references/prompt.md](prompt.md)
- [references/research/2512.24601v1.pdf](research/2512.24601v1.pdf)
- [references/research/summary.md](research/summary.md)
- [references/research-summary.md](research-summary.md)
- [references/rlm-audit.md](rlm-audit.md)
- [references/rlm-bootstrap-guide.md](rlm-bootstrap-guide.md)
- [references/rlm-cleanup-agent-acceptance-criteria.md](rlm-cleanup-agent-acceptance-criteria.md)
- [references/rlm-cleanup-agent.md](rlm-cleanup-agent.md)
- [references/rlm-curator-acceptance-criteria.md](rlm-curator-acceptance-criteria.md)
- [references/rlm-curator-fallback-tree.md](rlm-curator-fallback-tree.md)
- [references/rlm-curator.md](rlm-curator.md)
- [references/rlm-distill-agent-acceptance-criteria.md](rlm-distill-agent-acceptance-criteria.md)
- [references/rlm-distill-agent.md](rlm-distill-agent.md)
- [references/rlm-init-acceptance-criteria.md](rlm-init-acceptance-criteria.md)
- [references/rlm-init.md](rlm-init.md)
- [references/rlm-search-acceptance-criteria.md](rlm-search-acceptance-criteria.md)
- [references/rlm-search.md](rlm-search.md)
- [references/workflow.mmd](workflow.mmd)

## Scripts and verification

- [scripts/audit_cache.py](../scripts/audit_cache.py)
- [scripts/check_cached.py](../scripts/check_cached.py)
- [scripts/cleanup_cache.py](../scripts/cleanup_cache.py)
- [scripts/constants.py](../scripts/constants.py)
- [scripts/debug_rlm.py](../scripts/debug_rlm.py)
- [scripts/distill_one.py](../scripts/distill_one.py)
- [scripts/distiller.py](../scripts/distiller.py)
- [scripts/inject_summary.py](../scripts/inject_summary.py)
- [scripts/inventory.py](../scripts/inventory.py)
- [scripts/query_cache.py](../scripts/query_cache.py)
- [scripts/rlm_config.py](../scripts/rlm_config.py)
- [scripts/swarm_run.py](../scripts/swarm_run.py)
- [scripts/test_agent_memory_scripts.py](../scripts/test_agent_memory_scripts.py)

## Executable assets and templates

- [assets/examples/rlm_profiles.json](../assets/examples/rlm_profiles.json)
- [assets/examples/rlm_summary_cache_manifest.json](../assets/examples/rlm_summary_cache_manifest.json)
- [assets/examples/rlm_tools_manifest.json](../assets/examples/rlm_tools_manifest.json)
- [assets/jobs/distill_wiki.job.md](../assets/jobs/distill_wiki.job.md)
- [assets/templates/distiller_manifest.json](../assets/templates/distiller_manifest.json)
- [assets/templates/manifest-index.json](../assets/templates/manifest-index.json)
- [assets/templates/prompts/rlm/rlm_summarize_general.md](../assets/templates/prompts/rlm/rlm_summarize_general.md)
- [assets/templates/prompts/rlm/rlm_summarize_tool.md](../assets/templates/prompts/rlm/rlm_summarize_tool.md)
- [assets/templates/rlm_manifest.json](../assets/templates/rlm_manifest.json)
- [assets/templates/rlm_summary.md.j2](../assets/templates/rlm_summary.md.j2)

## Dependencies

- [requirements.in](../requirements.in)
- [requirements.txt](../requirements.txt)
