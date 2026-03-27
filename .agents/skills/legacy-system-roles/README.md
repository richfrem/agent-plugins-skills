# legacy-system-roles

Workflows for documenting and analyzing Oracle application security roles.

## Workflows

| Command | Purpose |
|---|---|
| `/legacy-system-roles_codify-role` | Create or update documentation for a specific role |
| `/legacy-system-roles_investigate-role` | Deep-dive analysis of a single role's permissions and usage |
| `/legacy-system-roles_investigate-roles` | Survey all roles in the system |
| `/legacy-system-roles_investigate-form-roles` | Ensure every role used in a Form is fully documented |

## Scripts

| Script | Purpose |
|---|---|
| `split_roles.py` | Split the roles source file into individual role records |
| `generate_role_inventory.py` | Build / refresh the `roles_inventory.json` |
| `capture_role_profile.py` | Capture a full role profile from the database |
| `fix_invalid_role_links.py` | Repair broken role cross-references in documentation |

## Assets

- `assets/base-role-manifest.json` — Base context manifest template for role investigations
- `assets/templates/role-template.md` — Standard role documentation template

## References

- `references/diagrams/workflows/role-discovery.mmd` — Role investigation workflow
