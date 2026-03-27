# legacy-system-oracle-forms

Specialized workflows for codifying and investigating Oracle Forms components — Forms, Libraries, Menus, and Object Libraries.

## Workflows

### Codify
| Command | Purpose |
|---|---|
| `/legacy-system-oracle-forms_codify-form` | Full documentation for an Oracle Form (.fmb) |
| `/legacy-system-oracle-forms_codify-library` | Full documentation for a PL/SQL Library (.pll) |
| `/legacy-system-oracle-forms_codify-menu` | Full documentation for a Menu Module (.mmb) |
| `/legacy-system-oracle-forms_codify-olb` | Full documentation for an Object Library (.olb) |
| `/legacy-system-oracle-forms_codify-report` | Full documentation for an Oracle Report (.rdf) |

### Investigate
| Command | Purpose |
|---|---|
| `/legacy-system-oracle-forms_investigate-form` | Deep-dive analysis of a Form's structure and logic |
| `/legacy-system-oracle-forms_investigate-library` | Analyze a Library's dependencies and API |
| `/legacy-system-oracle-forms_investigate-menu` | Analyze Menu items, roles, and navigation |
| `/legacy-system-oracle-forms_investigate-olb` | Analyze an Object Library's contents |
| `/legacy-system-oracle-forms_investigate-report` | Analyze an Oracle Report's queries and structure |
| `/legacy-system-oracle-forms_investigate-lineage` | Trace Form reachability from the application menu |
| `/legacy-system-oracle-forms_investigate-ui-menu` | Extract detailed UI menu configuration |

## Scripts

| Script | Purpose |
|---|---|
| `xml_miner.py` | Extract structured logic from Form XML exports |
| `pll_miner.py` | Extract API and globals from PLL text dumps |
| `mmb_miner.py` / `menu_miner.py` | Extract menu structure from MMB exports |
| `olb_miner.py` | Extract object definitions from OLB exports |
| `menu_xml_miner.py` | Extract menu logic from XML |
| `valid_form_ids.py` | Validate Form IDs against the known inventory |
| `search_for_open_form_references.py` | Find OPEN_FORM / CALL_FORM references across all forms |
| `report_miner.py` | Extract queries, parameters, triggers, and dependencies from Report XML exports |
| `count_forms.py` | Count forms in a directory |

## References

- `references/diagrams/workflows/form-discovery.mmd` — Form investigation workflow
- `references/diagrams/workflows/library-discovery.mmd` — Library investigation workflow
- `references/diagrams/workflows/menu-discovery.mmd` — Menu investigation workflow
- `references/diagrams/workflows/olb-discovery.mmd` — OLB investigation workflow
- `references/diagrams/workflows/report-discovery.mmd` — Report investigation workflow
