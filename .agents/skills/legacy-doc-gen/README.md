# legacy-doc-gen

Batch documentation generator for legacy system components. Factory engine for generating, enriching, and auditing Markdown overview files at scale.

## Scripts

### Batch Generation
| Script | Purpose |
|---|---|
| `batch_output_forms_overviews.py` | Generate Markdown overviews for all Forms |
| `batch_output_libraries_overviews.py` | Generate overviews for all PLL Libraries |
| `batch_output_menus_overviews.py` | Generate overviews for all Menus |
| `batch_output_olb_overviews.py` | Generate overviews for all Object Libraries |
| `batch_output_reports_overviews.py` | Generate overviews for all Reports |
| `batch_process_reports.py` | Orchestrate ReportMiner to batch-process report XML files and generate Report Overview docs |
| `batch_output_db_objects_overviews.py` | Generate overviews for DB objects |
| `batch_enrich_db_overviews.py` | Enrich DB documentation with latest analysis |
| `generate_missing_overviews.py` | Targeted generation for missing artifacts only |
| `enrich_links_v2.py` | Enrich cross-reference links using the master object collection |

### Auditing & Status
| Script | Purpose |
|---|---|
| `report_doc_status.py` | Report documentation coverage across all components |
| `audit_template_compliance.py` | Check overviews against the official template |
| `analyze_tracking_status.py` | Analyze AI analysis tracking status |
| `summarize_unanalyzed_forms.py` | List Forms not yet processed by AI |
| `count_overviews.py` | Count generated overview files |
| `generate_todo_list.py` | Generate a prioritized documentation TODO list |
| `update_analysis_tracking.py` | Update tracking flags after analysis completes |

### Utilities
| Script | Purpose |
|---|---|
| `config_manager.py` | Manage batch generation configuration |
| `overview_manager.py` | CRUD operations on overview files |
| `generate_docs_manifest.py` | Build a manifest of all generated documentation |
| `standardize_manifests.py` | Normalize manifest format across all doc sets |
