# Architectural Fitness & Precedence Rules

This document establishes the canonical Architectural Fitness Function rules, Truth Precedence, and boundary locks for all reengineering operations within the `exploration-cycle-plugin` environment. All agents and automated refactoring pipelines must strictly validate their work against these rules.

---

## 1. Truth Precedence Hierarchy

To prevent semantic drift, conflicting specifications, and design decay, the following strict hierarchy of truth is established. In any conflict, the higher-numbered level dominates:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. specs/REQS.md (Canonical Business Truth)                  │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. tests/characterization/ (Canonical Behavioral Truth)      │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. /domain model (Canonical Architectural Truth)            │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. handoff/spec docs (Derived Artifacts)                     │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Prototype Code (Exploratory Evidence Only)               │
└─────────────────────────────────────────────────────────────┘
```

1. **`specs/REQS.md` (Canonical Business Truth):** The ultimate source of business logic, invariant equations, terminology, and constraints. If code differs from `REQS.md`, the code is considered broken unless the human architect explicitly updates `REQS.md`.
2. **`tests/characterization/` (Canonical Behavioral Truth):** Executable assertion of behavior. Generated specs may never override executable behavioral evidence captured in characterization tests.
3. **`/domain` model (Canonical Architectural Truth):** Represents the pure domain model, entities, value objects, and domain exceptions. 
4. **Handoff/Spec docs:** Derived and synthesized artifacts for engineers.
5. **Prototype Code:** Exploratory evidence only. The prototype is **never** the source of truth, only evidence that a feature's basic flow was explored.

### 1.1 Truth Conflict Detector Protocol
Before any slice can be certified, a formal cross-reference check must verify that assertions in `tests/characterization/` do not silently contradict quantitative validation bounds or definitions inside `specs/REQS.md`. 
*   **Conflict Trigger:** If a characterization test passes against legacy behavior that `REQS.md` explicitly prohibits or restricts, a truth conflict is triggered.
*   **Resolution Gate:** The conflict must be logged as `HUMAN_REQUIRED` in the ambiguity ledger. The lower-precedence artifact must be refactored to align with the higher-precedence artifact, or a human architect must sign off on an exception.

---

## 2. Layered Architecture & Import Boundaries

To ensure clean architecture and avoid framework, UI, or database leakage, the following static import rules are continuously audited by the `domain-purity-auditor`:

### 2.1 Core Domain Layer (`/domain`)
The domain layer holds pure business logic. It must remain 100% technology-agnostic and network-agnostic.
* **Forbidden Imports / Symbols:**
  - UI Frameworks: `react`, `vue`, `svelte`, `angular`, `@angular/*`, `useState`, `useEffect`, `jsx`, `tsx` (containing UI markup)
  - HTTP/Server/Routing: `express`, `koa`, `fastify`, `nest`, `router`, `req`, `res`, `http`, `cors`
  - ORM/Database Clients: `prisma`, `sequelize`, `typeorm`, `mongoose`, `pg`, `mysql2`, `select *`, `insert into`, `connect()`, `Client()`
  - Vendor/Platform SDKs: `aws-sdk`, `@google-cloud/*`, `firebase-admin`, `@stripe/*`, `stripe`
  - I/O & Networking: `axios`, `fetch`, `http`, `fs`, `node:fs`, `node:http`, `node:https` (domain must use Port interface abstractions instead)
* **Coupling Rules:**
  - May *only* import from other domain sub-folders or pure, mathematical shared utility helpers (e.g. `/shared-pure`).
  - Zero dependencies on external layers (`/application`, `/infrastructure`, `/presentation`, or `/node_modules` dependencies outside pure helper libraries).

### 2.2 Application Layer (`/application`)
The application layer coordinates user stories, orchestrates domain flows, and handles use cases.
* **Forbidden Imports:**
  - UI Frameworks: `react`, `vue`, `svelte`, `angular`
  - Direct database client instances (e.g. concrete `prisma` client initialization; must use Port interfaces and receive Repository adapters via Dependency Injection).
* **Coupling Rules:**
  - May import from `/domain`.
  - Zero dependencies on `/infrastructure` or `/presentation` concrete implementations.

### 2.3 Presentation Layer (`/presentation`)
The presentation layer handles HTTP endpoints, UI components, CLI routers, and serialization.
* **Forbidden Imports & Access:**
  - **May NOT access database directly** (must call Application use cases).
  - May NOT bypass application services to execute core domain rules.
* **Coupling Rules:**
  - May import from `/application` and `/domain`.

---

## 3. Autonomous Rewrite Boundaries

AI agents are strictly forbidden from rewriting the following categories autonomously. 

### 3.1 Absolute Category Block (Pre-emption Rules)
This designation is an **absolute category block**. It pre-empts and completely overrides any numeric coupling risk score. Even if a vertical slice has low coupling and high test coverage, it **MUST be blocked from autonomous write operations** if it matches any of the following paths, filenames, symbols, imports, or behaviors:

1. **Authentication & Authorization:** Paths containing `auth`, `login`, `session`, `jwt`, `oauth`, `saml`. Content referencing `JWT`, `bcrypt`, `argon2`, `pbkdf2`, `session cookie`, `OAuth token`, `access control list`.
2. **Financial Calculations & Billing:** Paths containing `billing`, `payment`, `invoice`. Content referencing `payment intent`, `card number`, `stripe`, `@stripe/*`.
3. **Cryptography & Security:** Paths containing `crypto`, `hash`, `encrypt`. Content referencing `encryption key`, `salt generator`, `key rotation`, `cipher`.
4. **Compliance & Auditing:** Paths containing `compliance`, `pii`, `audit`, `gdpr`, `hipaa`. Content referencing regulatory logs or personal identification tracking.

### 3.2 Human Approval Bindings
No changes inside these forbidden categories can proceed without a valid `human-approval.json` file in the workspace. This file must include:
*   `approver`: Name of human architect.
*   `approved_files`: Specific file paths approved.
*   `approved_operation`: Exact description of the change.
*   `artifact_version`: Cryptographic or file content hash at the time of approval.
*   `expiry_condition`: The approval expires immediately if the target file contents are changed after approval.

---

## 4. Enforcement Protocols

1. **Pre-Commit Gate:** The `domain-purity-auditor` must run a static analysis search before any vertical slice migration is certified.
2. **Drift Check:** The `semantic-drift-auditor` must scan changed symbols against `specs/REQS.md` to ensure business terminology is intact.
3. **Slice Certification:** A slice cannot be certified (`slice-certified: true`) if it violates any import rule or truth precedence.
