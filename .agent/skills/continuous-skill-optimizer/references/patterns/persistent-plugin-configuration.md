# Pattern: Persistent Plugin Configuration with Interactive Fallback

## Overview
A state management pattern where an agent relies on a stable local JSON file for org-specific context across sessions, but features an interactive "setup interview" if the file is missing.

## Core Mechanic
Commands depend on variables in `settings.local.json` (e.g., approval chains, compliance frameworks). 
Two paths converge:
1. **Tier 1 (Persistent)**: Read silently from `settings.local.json` at session start.
2. **Tier 2 (Fallback)**: If missing, conduct a HITL (Human-in-the-Loop) interview to gather the data, then *save it* to `settings.local.json`.

This turns HITL from a recurring tax on every invocation into a one-time onboarding ceremony.

## Use Case
Plugins whose commands require stable, personalized context (org structure, tech stack, codebase path mapping) that is tedious to supply on every run.
