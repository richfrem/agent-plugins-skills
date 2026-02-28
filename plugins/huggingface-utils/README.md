# HuggingFace Utils Plugin 🤗

Integration utilities for syncing the Project Sanctuary Soul dataset with the HuggingFace Hub.

## Overview
This plugin provides the necessary skills and scripts to persist cognitive continuity data, RLM cache states, and deterministic traces up to a remote HuggingFace repository (the "Soul"), ensuring no agent learnings are lost between sessions.

## Core Capabilities
| Skill | Purpose |
| :--- | :--- |
| **hf-init** | Initialization script to validate connection and repo structure. |
| **forge-soul-exporter** | Gathers local traces and snapshot files and uploads them to the Hub. |

## Usage
These utilities are primarily invoked autonomously by the `guardian` Sub-Agent during the **Phase VII (Soul Persistence)** sequence of the session closure loop.
