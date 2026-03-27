# Pattern: Audience-Segmented Information Filtering

## Overview
A structural rule that dictates not just *how* something is said (tone) but explicitly *what facts are disclosed or withheld* based on the target audience.

## Core Mechanic
The skill contains an `Audience Policy Matrix` establishing what information is included and excluded per audience type.

```markdown
| Audience | Include | Exclude |
|----------|---------|---------|
| Exec     | Risk, decisions | Technical details |
| Eng      | Technical details | Strategic fluff |
```
The agent consults this table *before* generation, acting as an information checkpoint rather than a stylistic formatter.

## Use Case
Stakeholder updates, release notes, and status reports that are distributed to groups with divergent access needs or technical fluency.
