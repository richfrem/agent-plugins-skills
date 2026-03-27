---
name: legacy-system-business-rules
description: Workflows for discovering, investigating, and codifying business logic. Use this skill to register new Business Rules (BR-XXXX) or consolidate duplicates.
---

# Business Rules Management

## Overview

This skill helps manage the repository of Business Rules extracted from the legacy system.

## Available Workflows

### Discovery & Registration
- `/legacy-system-business-rules_investigate-business-rule`: Search for existing rules before creating new ones.
- `/legacy-system-business-rules_codify-business-rule`: Create a new BR-XXXX file using the standard template.

### Maintenance
- `/legacy-system-business-rules_consolidate-business-rules`: Merge duplicate or related rules into a single definition.

## Usage

Always start with `investigate` to avoid duplication.
