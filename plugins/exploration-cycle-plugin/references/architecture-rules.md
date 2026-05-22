# Architectural Fitness & Precedence Rules

This document establishes the canonical Architectural Fitness Function rules and Truth Precedence for all reengineering operations within the `exploration-cycle-plugin` environment. All agents and automated refactoring pipelines must strictly validate their work against these rules.

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

---

## 2. Layered Architecture & Import Boundaries

To ensure clean architecture and avoid framework, UI, or database leakage, the following static import rules are continuously audited by the `domain-purity-auditor`:

### 2.1 Core Domain Layer (`/domain`)
The domain layer holds pure business logic. It must remain 100% technology-agnostic.
* **Forbidden Imports:**
  - UI Frameworks: `react`, `vue`, `svelte`, `angular`, `@angular/*`
  - HTTP/Server Frameworks: `express`, `koa`, `fastify`, `nest`
  - ORM/Database Adapters: `prisma`, `sequelize`, `typeorm`, `mongoose`, `pg`, `mysql2`
  - Vendor/Platform SDKs: `aws-sdk`, `@google-cloud/*`, `firebase-admin`
  - I/O & Networking: `axios`, `fetch`, `http`, `fs` (use abstraction interfaces instead)
* **Coupling Rules:**
  - May *only* import from other domain sub-folders.
  - Zero dependencies on external layers (`/application`, `/infrastructure`, `/presentation`).

### 2.2 Application Layer (`/application`)
The application layer coordinates user stories, orchestrates domain flows, and handles use cases.
* **Forbidden Imports:**
  - UI Frameworks: `react`, `vue`, `svelte`, `angular`
  - Direct database clients (e.g. `prisma` client initialization; must use Port interfaces and receive Repository adapters via Dependency Injection).
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

AI agents are strictly forbidden from rewriting the following categories autonomously. If any changes are needed in these files/routes, they **MUST be marked AUTONOMOUS_REWRITE_FORBIDDEN** and require manual human validation:

1. **Authentication & Authorization (`/auth`, `/jwt`, sessions, OAuth login flows).**
2. **Financial Calculations & Billing (`/billing`, payment gateway integrations, math modules).**
3. **Cryptography & Security (`/crypto`, hashing, salt generators, key rotations).**
4. **Compliance & Auditing (`/audit`, regulatory logging, data retention rules).**

---

## 4. Enforcement Protocols

1. **Pre-Commit Gate:** The `domain-purity-auditor` must run a static analysis search before any vertical slice migration is certified.
2. **Drift Check:** The `semantic-drift-auditor` must scan changed symbols against `specs/REQS.md` to ensure business terminology is intact.
3. **Slice Certification:** A slice cannot be certified (`slice-certified: true`) if it violates any import rule or truth precedence.
