---
name: legacy-doc-gen
description: Batch documentation generator for legacy system components.
---

# Legacy Document Generator

## Overview

This skill provides bulk operations for generating, updating, and auditing documentation overviews. It is the factory engine behind the `legacy-system-oracle-forms` workflows.

## Key Scripts

### Batch Generation
- `scripts/batch_output_forms_overviews.py`: Generate Markdown overviews for all Forms.
- `scripts/batch_enrich_db_overviews.py`: Enrich DB documentation with latest analysis.
- `scripts/generate_missing_overviews.py`: Targeted generation for missing artifacts.
- `scripts/enrich_links_v2.py`: Enriches markdown documentation links using the master object collection.

### Auditing & Reporting
- `scripts/report_doc_status.py`: Generate a status report of documentation coverage.
- `scripts/audit_template_compliance.py`: Check if overviews match the official template.
- `scripts/summarize_unanalyzed_forms.py`: List forms that haven't been processed by AI yet.

## Usage

These scripts are typically run via the CLI or invoked by higher-level workflows.
