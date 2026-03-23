# [0015] Standardize all plugin templates to .jinja format

## Objective
Convert all template files across the plugin ecosystem to use the `.jinja` extension and Jinja2 templating syntax, consistent with the pattern already established in `agent-plugin-analyzer/assets/templates/`.

## Acceptance Criteria
- [ ] Audit all plugins for template files not using the `.jinja` extension.
- [ ] Rename template files to add the `.jinja` extension (e.g. `README.md` → `README.md.jinja`).
- [ ] Convert placeholder syntax to Jinja2 style (`{name}` → `{{ name }}`, conditionals use `{% if %}` blocks).
- [ ] Update any scaffolding scripts that reference the old template filenames.
- [ ] Verify `create-plugin` and `create-skill` scaffolders correctly read `.jinja` files and write rendered output.

## Notes
- **Why this is needed:** Template files without the `.jinja` extension are ambiguous — they look like real output files rather than templates, making the codebase harder to navigate and the scaffolding intent unclear.
- **Reference pattern:** `plugins/agent-plugin-analyzer/assets/templates/README.md.jinja` is the target convention.
- **Jinja2 benefits over bare `{placeholder}` syntax:** supports conditionals (`{% if has_scripts %}`), loops (`{% for skill in skills %}`), and filters — enabling one template to generate varied outputs without multiple template files.
- Coordinate with `create-plugin` and `create-skill` skills to ensure they render via Jinja2 (requires `jinja2` in `requirements.in` if not already present).
