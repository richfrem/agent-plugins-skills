# Acceptance Criteria: vibe-slice-migrator

## Correct Behaviors

- **Correct:** Vibe-slice-migrator migrates the legacy codebase progressively slice-by-slice instead of using a big-bang rewrite.
- **Correct:** Vibe-slice-migrator isolates business logic into Domain and Application layers, exposing interfaces (ports) for infrastructure adapters.
- **Correct:** Vibe-slice-migrator implements concrete database and routing adapters under an `/infrastructure/` directory.
- **Correct:** Vibe-slice-migrator verifies each migrated slice using the generated safety-net characterization tests.
- **Correct:** Vibe-slice-migrator deprecates or removes dead legacy code after verification is fully complete.

## Incorrect Behaviors

- **Incorrect:** Vibe-slice-migrator compromises architectural boundaries by letting domain or application use-case files import concrete databases or controllers.
- **Incorrect:** Vibe-slice-migrator migrates code without running the characterization tests or ignores test failures.
- **Incorrect:** Vibe-slice-migrator breaks the application by deleting multiple features before verifying the clean implementation.
