# Acceptance criteria

Each selected skill must run independently from its own scripts and assets.
Preserve consumer profiles and raw source data. Run a focused dry run before writes.
If dependencies or profiles are unavailable, report the exact missing prerequisite;
do not silently switch engines, overwrite configuration, or bypass write authorization.

This is the package-wide distribution contract. The public skills own their
behavioral acceptance indexes under their own references folders; this file does
not contain a skill-specific interview, script or operational workflow.
