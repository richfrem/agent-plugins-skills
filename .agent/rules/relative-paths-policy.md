# Relative Paths Policy

## Rules

### 1. All file references must be relative to the skill folder

File references in commands and skill workflows must use paths relative to the skill's root directory, not absolute paths or paths relative to the repository root.

**Correct:**
```
../references/diagrams/workflows/olb-discovery.mmd
../scripts/olb_miner.py
../assets/templates/forms-sops/sop-codify-olb-template.md
```

**Incorrect:**
```
docs/diagrams/workflows/olb-discovery.mmd
plugins/legacy system/scripts/olb_miner.py
C:\Users\...\olb_miner.py
```

The `../` prefix is used because commands live in a `commands/` subdirectory of the skill, so one level up (`../`) reaches the skill root.

### 2. All content required by a skill must live inside that skill's folder

Every file a skill references must be present inside the skill's directory — either as a hard copy or a symlink. A skill must be fully self-contained.

**Required layout:**
```
skills/<skill-name>/
├── SKILL.md
├── commands/          <- workflow command files
├── references/        <- diagrams, policies, acceptance criteria
│   └── diagrams/
│       └── workflows/
├── scripts/           <- Python/JS helper scripts
└── assets/
    └── templates/     <- output templates
```

Do not reference files outside the skill folder from within a command. If a shared asset is needed, copy or symlink it into the skill directory before use.

### 3. Symlinks and hard copies inside a skill folder are authoritative

The copy of a file inside the skill's directory is the authoritative version at runtime. The source in `plugins/<plugin>/assets/` or `plugins/<plugin>/scripts/` is the origin — changes must propagate to the skill copies via the bridge installer or manual sync.

### 4. Install locations

Skills are installed by `bridge_installer.py` into:
- `.agents/skills/<skill-name>/`  (canonical)
- `.agent/skills/<skill-name>/`
- `.claude/skills/<skill-name>/`

After installation, relative paths inside commands resolve from the skill root at the installed location. Verify paths against the installed structure, not the source tree.
