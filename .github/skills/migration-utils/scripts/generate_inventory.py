import json
import os
import sys
from pathlib import Path

# Add project root to sys.path to find plugins package
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Known mappings from MIGRATION_GUIDE.md and analysis
KNOWN_MAPPINGS = {
    # Vector DB
    "tools/codify/vector/ingest.py": "plugins/vector-db/scripts/ingest.py",
    "tools/retrieve/vector/query.py": "plugins/vector-db/scripts/query.py",
    "tools/curate/vector/cleanup.py": "plugins/vector-db/scripts/cleanup.py",
    "tools/codify/vector/ingest_code_shim.py": "plugins/vector-db/scripts/ingest_code_shim.py",

    # RLM
    "tools/codify/rlm/distiller.py": "plugins/rlm-factory/scripts/distiller.py",
    "tools/retrieve/rlm/query_cache.py": "plugins/rlm-factory/scripts/query_cache.py",
    "tools/retrieve/rlm/inventory.py": "plugins/rlm-factory/scripts/inventory.py", # Moved to rlm-factory based on ls output
    
    # Tool Inventory
    "tools/curate/inventories/manage_tool_inventory.py": "plugins/tool-inventory/scripts/manage_tool_inventory.py",
    "tools/codify/rlm/rlm_config.py": "plugins/tool-inventory/scripts/rlm_config.py", # Reasonable guess
    "tools/curate/rlm/cleanup_cache.py": "plugins/rlm-factory/scripts/cleanup_cache.py", # Corrected destination based on ls output

    # Link Checker
    "tools/codify/documentation/check_broken_paths.py": "plugins/link-checker/scripts/check_broken_paths.py",
    "tools/codify/documentation/map_repository_files.py": "plugins/link-checker/scripts/map_repository_files.py",
    "tools/curate/link-checker/check_broken_paths.py": "plugins/link-checker/scripts/check_broken_paths.py", # Duplicate
    "tools/curate/link-checker/map_repository_files.py": "plugins/link-checker/scripts/map_repository_files.py", # Duplicate
    "tools/curate/link-checker/smart_fix_links.py": "plugins/link-checker/scripts/smart_fix_links.py",

    # Context Bundler
    "tools/retrieve/bundler/bundle.py": "plugins/context-bundler/scripts/bundle.py",
    "tools/retrieve/bundler/manifest_manager.py": "plugins/context-bundler/scripts/manifest_manager.py",
    "tools/investigate/utils/path_resolver.py": "plugins/context-bundler/scripts/path_resolver.py",
    "tools/utils/path_resolver.py": "plugins/context-bundler/scripts/path_resolver.py",

    # Spec Kitty / Bridge
    "tools/bridge/speckit_system_bridge.py": "plugins/spec-kitty/scripts/speckit_system_bridge.py",
    "tools/bridge/sync_workflows.py": "plugins/spec-kitty/scripts/sync_workflows.py",
    "tools/bridge/sync_rules.py": "plugins/spec-kitty/scripts/sync_rules.py",
    "tools/bridge/sync_skills.py": "plugins/spec-kitty/scripts/sync_skills.py",
    "tools/bridge/verify_bridge_integrity.py": "plugins/spec-kitty/scripts/verify_bridge_integrity.py",

    # Mermaid
    "tools/codify/diagrams/export_mmd_to_image.py": "plugins/mermaid-export/scripts/export_mmd_to_image.py",

    # Agent Orchestrator
    "plugins/spec-kitty/scripts/agent_orchestrator.py": "plugins/agent-orchestrator/scripts/agent_orchestrator.py", # inferred
    
    # ADR Manager
    "tools/investigate/utils/next_number.py": "plugins/adr-manager/scripts/next_number.py",
    
    # Code Snapshot (New?)
    "tools/snapshot_utils.py": "plugins/code-snapshot/scripts/snapshot_utils.py", # Guess

    # --- Second Wave Moves (Refinement) ---
    # Legacy System Roles
    "plugins/inventory-manager/scripts/generate_role_inventory.py": "plugins/legacy-system-roles/scripts/generate_role_inventory.py",
    "plugins/legacy-doc-gen/scripts/capture_role_profile.py": "plugins/legacy-system-roles/scripts/capture_role_profile.py",
    "plugins/link-checker/scripts/fix_invalid_role_links.py": "plugins/legacy-system-roles/scripts/fix_invalid_role_links.py",
    "plugins/temporary-scripts/scripts/split_roles.py": "plugins/legacy-system-roles/scripts/split_roles.py",
    
    # Dependency Analysis
    "plugins/dependency-analysis/workflows/investigate-direct-dependencies.md": "plugins/dependency-analysis/workflows/investigate-direct-dependencies.md", # No rename
    
    # Inventory Manager
    ".agent/workflows/legacy-system/inventories/curate-inventories.md": "plugins/inventory-manager/workflows/curate-inventories.md",

    # ADR Manager
    ".agent/workflows/utilities/adr-manage.md": "plugins/adr-manager/workflows/adr-manage.md",
    ".agent/workflows/utilities/adrs-manage.md": "plugins/adr-manager/workflows/adrs-manage.md",

    # Context Bundler
    ".agent/workflows/utilities/bundle-manage.md": "plugins/context-bundler/workflows/bundle-manage.md",

    # Task Manager
    ".agent/workflows/utilities/tasks-manage.md": "plugins/task-manager/workflows/tasks-manage.md",

    # Tool Inventory
    ".agent/workflows/utilities/tool-inventory-manage.md": "plugins/tool-inventory/workflows/tool-inventory-manage.md",

    # Link Checker
    ".agent/workflows/utilities/post-move-link-check.md": "plugins/link-checker/workflows/post-move-link-check.md",

    # Business Rules
    ".agent/workflows/legacy-system/business-rules/codify-business-rule.md": "plugins/legacy-system-business-rules/workflows/codify-business-rule.md",
    ".agent/workflows/legacy-system/business-rules/consolidate-business-rules.md": "plugins/legacy-system-business-rules/workflows/consolidate-business-rules.md",
    ".agent/workflows/legacy-system/business-rules/investigate-business-rule.md": "plugins/legacy-system-business-rules/workflows/investigate-business-rule.md",

    # Business Workflows
    ".agent/workflows/legacy-system/business-workflows/codify-business-workflow.md": "plugins/legacy-system-business-workflows/workflows/codify-business-workflow.md",
    ".agent/workflows/legacy-system/business-workflows/investigate-business-workflow.md": "plugins/legacy-system-business-workflows/workflows/investigate-business-workflow.md",

    # Spec Kitty Workflows
    ".agent/workflows/spec-kitty.accept.md": "plugins/spec-kitty/workflows/spec-kitty.accept.md",
    ".agent/workflows/spec-kitty.analyze.md": "plugins/spec-kitty/workflows/spec-kitty.analyze.md",
    ".agent/workflows/spec-kitty.checklist.md": "plugins/spec-kitty/workflows/spec-kitty.checklist.md",
    ".agent/workflows/spec-kitty.clarify.md": "plugins/spec-kitty/workflows/spec-kitty.clarify.md",
    ".agent/workflows/spec-kitty.constitution.md": "plugins/spec-kitty/workflows/spec-kitty.constitution.md",
    ".agent/workflows/spec-kitty.dashboard.md": "plugins/spec-kitty/workflows/spec-kitty.dashboard.md",
    ".agent/workflows/spec-kitty.implement.md": "plugins/spec-kitty/workflows/spec-kitty.implement.md",
    ".agent/workflows/spec-kitty.merge.md": "plugins/spec-kitty/workflows/spec-kitty.merge.md",
    ".agent/workflows/spec-kitty.plan.md": "plugins/spec-kitty/workflows/spec-kitty.plan.md",
    ".agent/workflows/spec-kitty.research.md": "plugins/spec-kitty/workflows/spec-kitty.research.md",
    # Oracle DB Analysis
    "tools/codify/rlm/sql_dump_miner.py": "plugins/legacy-system-database/scripts/sql_dump_miner.py",
    "tools/curate/utils/split_sql_dump.py": "plugins/legacy-system-database/scripts/split_sql_dump.py",
    "tools/investigate/miners/extract_triggers.py": "plugins/legacy-system-database/scripts/extract_triggers.py",
    "tools/investigate/miners/granulate_sql.py": "plugins/legacy-system-database/scripts/granulate_sql.py",
    "tools/codify/enrichment/batch_enrich_db_objects.py": "plugins/legacy-system-database/scripts/batch_enrich_db_objects.py",
    "tools/codify/doc_gen/batch_create_trigger_overviews.py": "plugins/legacy-system-database/scripts/batch_create_trigger_overviews.py",
    "tools/codify/enrichment/batch_process_db_objects.py": "plugins/legacy-system-database/scripts/batch_process_db_objects.py",
    "tools/investigate/miners/db_miner.py": "plugins/legacy-system-database/scripts/db_miner.py",
    "tools/investigate/search/search_plsql.py": "plugins/legacy-system-database/scripts/search_plsql.py",

    # Oracle DB Analysis (Workflows)
    ".agent/workflows/legacy-system/investigate-code-search.md": "plugins/legacy-system-database/workflows/investigate-code-search.md",

    # Oracle Forms Analysis (Orchestrator)
    ".agent/workflows/legacy-system/codify-app.md": "plugins/legacy-system-oracle-forms/workflows/codify-app.md",

    # Legacy Doc Gen
    "tools/codify/doc_gen/analyze_tracking_status.py": "plugins/legacy-doc-gen/scripts/analyze_tracking_status.py",
    "tools/codify/doc_gen/audit_template_compliance.py": "plugins/legacy-doc-gen/scripts/audit_template_compliance.py",
    # ... (keeping existing lines)
    "tools/codify/doc_gen/update_analysis_tracking.py": "plugins/legacy-doc-gen/scripts/update_analysis_tracking.py",

    # --- Documentation Moves ---
    # Agent Orchestrator
    "docs/architecture/agent-architecture.md": "plugins/agent-orchestrator/docs/agent-architecture.md",
    "docs/architecture/multi_agent_relationship.mmd": "plugins/agent-orchestrator/docs/multi_agent_relationship.mmd",
    "docs/architecture/context_management_flow.mmd": "plugins/agent-orchestrator/docs/context_management_flow.mmd",
    
    # Coding Conventions
    "docs/standards/coding_conventions_policy.md": "plugins/coding-conventions/docs/coding_conventions_policy.md",
    "docs/standards/file-naming.md": "plugins/coding-conventions/docs/file-naming.md",
    
    # Forms Visualizer
    "docs/oracle-forms-visualizer/setup.md": "plugins/forms-visualizer/docs/setup.md",
    
    # Legacy System Oracle Forms
    "docs/architecture/legacy-oracle-architecture.mmd": "plugins/legacy-system-oracle-forms/docs/legacy-oracle-architecture.mmd",
    
    # Spec Kitty
    "docs/OPERATIONS.md": "plugins/spec-kitty/docs/OPERATIONS.md",
    "docs/architecture/workflow-architecture.md": "plugins/spec-kitty/docs/workflow-architecture.md",
    "docs/architecture/project_management_structure.mmd": "plugins/spec-kitty/docs/project_management_structure.mmd",
    "docs/architecture/spec-driven-development-lifecycle.mmd": "plugins/spec-kitty/docs/spec-driven-development-lifecycle.mmd",
    "docs/diagrams/speckit_system_bridge.mmd": "plugins/spec-kitty/docs/diagrams/speckit_system_bridge.mmd",
    "docs/diagrams/speckit_system_bridge.png": "plugins/spec-kitty/docs/diagrams/speckit_system_bridge.png",
    "docs/diagrams/agents/gemini-bridge-architecture.mmd": "plugins/spec-kitty/docs/diagrams/agents/gemini-bridge-architecture.mmd",
    "docs/diagrams/agents/gemini-bridge-architecture.png": "plugins/spec-kitty/docs/diagrams/agents/gemini-bridge-architecture.png",
    
    # Tool Inventory
    "docs/tools/Tool_Script_Organization_Strategy.md": "plugins/tool-inventory/docs/Tool_Script_Organization_Strategy.md",
    "docs/diagrams/tools/Tool_Architecture_Domain_Model.mmd": "plugins/tool-inventory/docs/diagrams/legacy-architecture/Tool_Architecture_Domain_Model.mmd",
    "docs/diagrams/tools/Tool_Architecture_Domain_Model.png": "plugins/tool-inventory/docs/diagrams/legacy-architecture/Tool_Architecture_Domain_Model.png",

    # RLM Factory
    "docs/diagrams/rlm/rlm_process.mmd": "plugins/rlm-factory/docs/diagrams/rlm_process.mmd",
    "docs/diagrams/architecture/rlm-factory-architecture.mmd": "plugins/rlm-factory/docs/diagrams/architecture/rlm-factory-architecture.mmd",
    "docs/diagrams/architecture/rlm-factory-architecture.png": "plugins/rlm-factory/docs/diagrams/architecture/rlm-factory-architecture.png",
    "docs/diagrams/architecture/rlm-factory-dual-path.mmd": "plugins/rlm-factory/docs/diagrams/architecture/rlm-factory-dual-path.mmd",
    "docs/diagrams/architecture/rlm-factory-dual-path.png": "plugins/rlm-factory/docs/diagrams/architecture/rlm-factory-dual-path.png",

    # AI Resources
    "tools/ai-resources/prompts/": "plugins/ai-resources/prompts/",
    "tools/ai-resources/personas/": "plugins/ai-resources/personas/",

    # Standalone Docs
    "docs/tools/standalone/context-bundler/": "plugins/context-bundler/docs/",
    "docs/tools/standalone/link-checker/": "plugins/link-checker/docs/",
    "docs/tools/standalone/rlm-factory/": "plugins/rlm-factory/docs/",
    "docs/tools/standalone/vector-db/": "plugins/vector-db/docs/",
    "docs/tools/standalone/xml-to-markdown/": "plugins/xml-to-markdown/docs/",

    # Diagram Moves
    # Database
    "docs/diagrams/workflows/db-*.mmd": "plugins/legacy-system-database/docs/diagrams/workflows/db-*.mmd",
    "docs/diagrams/workflows/db-*.png": "plugins/legacy-system-database/docs/diagrams/workflows/db-*.png",
    
    # Business Rules
    "docs/diagrams/workflows/business-rule-candidate-discovery.mmd": "plugins/legacy-system-business-rules/docs/diagrams/workflows/business-rule-candidate-discovery.mmd",
    "docs/diagrams/workflows/business-rule-candidate-discovery.png": "plugins/legacy-system-business-rules/docs/diagrams/workflows/business-rule-candidate-discovery.png",

    # Business Workflows
    "docs/diagrams/workflows/business-workflow-discovery.mmd": "plugins/legacy-system-business-workflows/docs/diagrams/workflows/business-workflow-discovery.mmd",

    # Roles
    "docs/diagrams/workflows/role-discovery.mmd": "plugins/legacy-system-roles/docs/diagrams/workflows/role-discovery.mmd",
    
    # Reports
    "docs/diagrams/workflows/report-discovery.mmd": "plugins/legacy-system-oracle-reports/docs/diagrams/workflows/report-discovery.mmd",
    "docs/diagrams/workflows/report-discovery.png": "plugins/legacy-system-oracle-reports/docs/diagrams/workflows/report-discovery.png",
    
    # Forms
    "docs/diagrams/workflows/form-*.mmd": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/form-*.mmd",
    "docs/diagrams/workflows/form-*.png": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/form-*.png",
    "docs/diagrams/workflows/library-discovery.mmd": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/library-discovery.mmd",
    "docs/diagrams/workflows/library-discovery.png": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/library-discovery.png",
    "docs/diagrams/workflows/menu-*.mmd": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/menu-*.mmd",
    "docs/diagrams/workflows/menu-*.png": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/menu-*.png",
    "docs/diagrams/workflows/menu_generation_pipeline.mmd": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/menu_generation_pipeline.mmd",
    "docs/diagrams/workflows/menu_generation_pipeline.png": "plugins/legacy-system-oracle-forms/docs/diagrams/workflows/menu_generation_pipeline.png",
}

# Paths to explicitly exclude from migration (they will be deleted later or handled manually)
EXCLUDE_PREFIXES = [
    "tools/standalone/",
    "tools/investment-screener/",  # Treat as separate app
]

def find_files(root_dir, skip_dirs=None, extensions=None):
    if skip_dirs is None:
        skip_dirs = []
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip
        dirs[:] = [d for d in dirs if d not in skip_dirs and d != '__pycache__']
        for file in files:
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue
            file_list.append(os.path.join(root, file))
    return file_list

def map_workflows():
    """Map .agent/workflows/*.md to plugins/*/commands/*.md"""
    workflow_files = find_files(".agent/workflows", extensions=[".md"])
    plugin_commands = find_files("plugins", extensions=[".md"])
    
    # Filter only commands/ directories in plugins
    plugin_commands = [p for p in plugin_commands if "/commands/" in p]
    
    mappings = {}
    
    # Create target map: command_name.md -> full_path
    target_map = {}
    for p in plugin_commands:
        name = os.path.basename(p)
        target_map[name] = p
        
    for wf in workflow_files:
        name = os.path.basename(wf)
        # Try exact match
        if name in target_map:
            mappings[wf] = target_map[name]
        else:
            # Try mapping common prefixes/names
            # e.g. manage-tool-inventory.md vs manage.md in tool-inventory plugin
            pass
            
    return mappings

def map_skills():
    """Map .agent/skills/<name> to plugins/*/skills/<name>"""
    # This is trickier because skills are directories.
    # We'll list top-level directories in .agent/skills
    skills_root = ".agent/skills"
    if not os.path.exists(skills_root):
        return {}
        
    agent_skills = [d for d in os.listdir(skills_root) if os.path.isdir(os.path.join(skills_root, d))]
    
    # Find skill directories in plugins
    # plugins/<plugin>/skills/<skill-name>
    plugin_skills = []
    for root, dirs, files in os.walk("plugins"):
        if "skills" in dirs:
            skills_dir = os.path.join(root, "skills")
            for sk in os.listdir(skills_dir):
                if os.path.isdir(os.path.join(skills_dir, sk)):
                    plugin_skills.append(os.path.join(skills_dir, sk))

    mappings = {}
    
    for askill in agent_skills:
        askill_path = os.path.join(skills_root, askill)
        
        # Try to find matching skill folder name
        # Note: plugin skill names might differ (e.g. dependency-management vs dependency-agent)
        
        # 1. Exact match of directory name
        match = next((p for p in plugin_skills if os.path.basename(p) == askill), None)
        
        # 2. Heuristic: Plugin name matches skill name
        if not match:
             # e.g. .agent/skills/dependency-management -> plugins/dependency-management/skills/*
             # check if any plugin has a name matching the skill
             for p_skill_path in plugin_skills:
                 # p_skill_path like plugins/dependency-management/skills/dependency-agent
                 parts = p_skill_path.split(os.sep)
                 if len(parts) >= 2:
                     plugin_name = parts[1] # plugins/<plugin_name>/...
                     if plugin_name == askill:
                         match = p_skill_path
                         break

        if match:
             # Map the directory itself
             mappings[askill_path] = match
             
             # Also map all files inside recursively
             for root, _, files in os.walk(askill_path):
                 for f in files:
                     src_file = os.path.join(root, f)
                     rel_from_skill = os.path.relpath(src_file, askill_path)
                     dest_file = os.path.join(match, rel_from_skill)
                     mappings[src_file] = dest_file

    return mappings

def generate_inventory():
    # tools_files = find_files("tools", ...) # DEPRECATED: Scanning references instead
    plugins_files = find_files("plugins", skip_dirs=[".git", "node_modules", "venv", ".venv"], extensions=[".py"])
    
    inventory = {}
    
    # Create potential targets map: filename -> full_path (Fallback)
    plugin_targets = {}
    for p in plugins_files:
        filename = os.path.basename(p)
        if filename not in plugin_targets:
            plugin_targets[filename] = []
        plugin_targets[filename].append(p)

    # --- TOOLS MAPPING ---
    # Load RLM Cache
    # We need to import from plugins.tool_inventory.scripts.query_cache
    # Since PROJECT_ROOT is in sys.path, we can import plugins...
    try:
        from plugins.tool_inventory.scripts.query_cache import load_cache, RLMConfig
    except ImportError:
        # Fallback: try adding specific path if package structure is loose
        tool_inv_path = os.path.join(PROJECT_ROOT, 'plugins', 'tool-inventory', 'scripts')
        if tool_inv_path not in sys.path:
            sys.path.append(tool_inv_path)
        from query_cache import load_cache, RLMConfig

    config = RLMConfig(run_type="tool")
    cache_data = load_cache(config)
    
    # Build filename -> new_path map from cache
    # Only map if new path is in plugins/
    cache_map = {}
    for path, entry in cache_data.items():
        if path.startswith("plugins/"):
            filename = os.path.basename(path)
            # Handle duplicates: if filename exists, mark as ambiguous (None)
            if filename in cache_map:
                cache_map[filename] = None 
            else:
                cache_map[filename] = path

    # --- REFERENCE SCANNING ---
    print("Scanning codebase for 'tools/' references...")
    import re
    
    # Regex to find tools/... references
    # Matches words starting with tools/ ending in .py, .md, .sh etc
    # We'll be generous and refine later
    ref_pattern = re.compile(r'tools/[\w\-\./]+\.[a-zA-Z]+')
    
    found_refs = set()
    
    # Scan all files in project
    all_files = find_files(".", skip_dirs=[".git", "node_modules", "venv", ".venv", "__pycache__", "coverage", "dist", "build"])
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = ref_pattern.findall(content)
                for m in matches:
                    # Filter out tools/cli.py valid usages
                    if m == "tools/cli.py": continue
                    found_refs.add(m)
        except Exception:
            continue
            
    print(f"Found {len(found_refs)} unique 'tools/...' references in codebase.")

    # --- RESOLUTION ---
    # Resolve found references against RLM Cache
    
    for tool_path in sorted(list(found_refs)):
        # Normalize path just in case
        rel_path = tool_path
        
        # Skip explicit exclusions
        if any(rel_path.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
            continue

        new_path = None
        status = "pending"
        
        # 1. Check known mappings first (Overrides)
        if rel_path in KNOWN_MAPPINGS:
            new_path = KNOWN_MAPPINGS[rel_path]
        else:
            # 2. Try to match by filename using RLM Cache
            filename = os.path.basename(rel_path)
            if filename in cache_map and cache_map[filename]:
                 new_path = cache_map[filename]
            else:
                 # 3. Fallback: Try to find file in plugins dir if cache missed it (e.g. new file)
                 if filename in plugin_targets:
                     candidates = plugin_targets[filename]
                     if len(candidates) == 1:
                         new_path = candidates[0]
            
        if new_path:
             if not os.path.exists(new_path):
                 status = "target_missing"
        else:
            status = "unmapped"
        
        inventory[rel_path] = {
            "new_path": new_path,
            "status": status
        }

    # --- WORKFLOWS MAPPING ---
    wf_mappings = map_workflows()
    for src, dst in wf_mappings.items():
        rel_src = os.path.relpath(src, ".")
        rel_dst = os.path.relpath(dst, ".")
        inventory[rel_src] = {
            "new_path": rel_dst,
            "status": "pending"
        }
        
    # Skills
    # Skills
    skills_map = {
        ".agent/skills/oracle-forms-tech-stack-mapping/SKILL.md": "plugins/code-conversion/skills/oracle-forms-tech-stack-mapping/SKILL.md",
        ".agent/skills/dependency-management/SKILL.md": "plugins/dependency-management/skills/dependency-management/SKILL.md",
        ".agent/skills/spec_kitty_workflow/SKILL.md": "plugins/spec-kitty/skills/spec_kitty_workflow/SKILL.md",
        ".agent/skills/coding-conventions/SKILL.md": "plugins/coding-conventions/skills/coding-conventions/SKILL.md",
        ".agent/skills/context-bundling/SKILL.md": "plugins/context-bundler/skills/context-bundling/SKILL.md",
        ".agent/skills/rlm-distill/SKILL.md": "plugins/rlm-factory/skills/rlm-distill/SKILL.md",
        ".agent/skills/vector-db-launch/SKILL.md": "plugins/vector-db/skills/vector-db-launch/SKILL.md",
        ".agent/skills/tool_discovery/SKILL.md": "plugins/tool-inventory/skills/tool_discovery/SKILL.md",
        ".agent/skills/ollama-launch/SKILL.md": "plugins/rlm-factory/skills/ollama-launch/SKILL.md",
        
        # Generic Skills
        ".agent/skills/code-review/SKILL.md": "plugins/code-review/skills/code-review/SKILL.md",
        ".agent/skills/doc-coauthoring/SKILL.md": "plugins/doc-coauthoring/skills/doc-coauthoring/SKILL.md",
        ".agent/skills/mcp-builder/SKILL.md": "plugins/mcp-builder/skills/mcp-builder/SKILL.md",
        ".agent/skills/memory-management/SKILL.md": "plugins/memory-management/skills/memory-management/SKILL.md",
        ".agent/skills/skill-creator/SKILL.md": "plugins/skill-creator/skills/skill-creator/SKILL.md",
        
        # Rules
        ".agent/rules/standard-workflow-rules.md": "plugins/spec-kitty/references/standard-workflow-rules.md",
    }
    
    for src, dst in skills_map.items():
        inventory[src] = {
            "new_path": dst,
            "status": "pending"
        }

    with open("migration_inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)
    
    print(f"Generated inventory for {len(inventory)} items.")

    
    # Print unmapped items for review
    unmapped = [k for k, v in inventory.items() if v['status'] == 'unmapped']
    if unmapped:
        print("\nUnmapped items:")
        for item in unmapped:
            print(f"  {item}")

if __name__ == "__main__":
    generate_inventory()
