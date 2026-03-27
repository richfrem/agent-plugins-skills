---
name: legacy-system-database
description: Specialized workflows for codifying and investigating Oracle Database schema objects. Use this skill when you need to analyze, document, or extract DDL/logic from Tables, Views, Packages, Procedures, Functions, and Triggers.
---

# Legacy System Database

## Overview

This skill provides access to the **legacy-system-database** plugin, specifically designed for deep analysis of the Oracle Database schema.

## Available Workflows

### Codify (Document & Analyze)
Create comprehensive documentation for database objects:

- `/legacy-system-database_codify-db-package`: Document a PL/SQL Package
- `/legacy-system-database_codify-db-procedure`: Document a Stored Procedure
- `/legacy-system-database_codify-db-function`: Document a Database Function
- `/legacy-system-database_codify-db-trigger`: Document a Database Trigger
- `/legacy-system-database_codify-db-view`: Document a Database View
- `/legacy-system-database_codify-db-table`: Document a Table structure
- `/legacy-system-database_codify-db-type`: Document a User-Defined Type
- `/legacy-system-database_codify-db-sequence`: Document a Sequence
- `/legacy-system-database_codify-db-constraint`: Document Constraints
- `/legacy-system-database_codify-db-index`: Document Indexes

### Investigate (Deep Dive)
Targeted analysis tools:

- `/legacy-system-database_investigate-code-search`: Search PL/SQL codebase
- `/legacy-system-database_investigate-db-package`: Analyze Package internals
- `/legacy-system-database_investigate-db-procedure`: Analyze Procedure logic
- `/legacy-system-database_investigate-db-function`: Analyze Function logic

## Usage

Invoke these workflows using the slash commands listed above. They handle context gathering using the RLM and Source Analysis tools automatically.
