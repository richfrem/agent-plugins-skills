---
name: legacy-system-oracle-forms
description: Specialized workflows for codifying and investigating Oracle Forms components. Use this skill when you need to analyze, document, or extract logic from Forms, Libraries, Menus, or Object Libraries.
---

# Legacy System Oracle Forms

## Overview

This skill provides access to the **legacy-system-oracle-forms** plugin, which contains specialized workflows for processing Oracle Forms artifacts.

## Available Workflows

### Codify (Document & Analyze)
Use these workflows to create comprehensive documentation for components:

- `/legacy-system-oracle-forms_codify-app`: Document a full Application
- `/legacy-system-oracle-forms_codify-form`: Document an Oracle Form (.fmb)
- `/legacy-system-oracle-forms_codify-library`: Document a PL/SQL Library (.pll)
- `/legacy-system-oracle-forms_codify-menu`: Document a Menu Module (.mmb)
- `/legacy-system-oracle-forms_codify-olb`: Document an Object Library (.olb)

### Investigate (Deep Dive)
Use these workflows for targeted analysis without full documentation:

- `/legacy-system-oracle-forms_investigate-form`: Analyze a Form's structure and logic
- `/legacy-system-oracle-forms_investigate-library`: Analyze a Library's dependencies
- `/legacy-system-oracle-forms_investigate-menu`: Analyze Menu items and roles
- `/legacy-system-oracle-forms_investigate-lineage`: Trace Form lineage and reachability
- `/legacy-system-oracle-forms_investigate-ui-menu`: Extract detailed UI menu structure

## Usage

These workflows are registered with the Agent Orchestrator. You can invoke them directly using the slash commands above.
