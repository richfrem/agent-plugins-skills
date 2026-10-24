# Acceptance Criteria: vibe-domain-extractor

## Correct Behaviors

- **Correct:** Vibe-domain-extractor identifies and isolates business calculations, invariants, and entities from express/database routers.
- **Correct:** Vibe-domain-extractor maps domain classes and value objects inside a structured `/domain/` folder.
- **Correct:** Vibe-domain-extractor ensures zero third-party I/O (Express, ORMs, HTTP fetches) is imported in `/domain` scripts.
- **Correct:** Vibe-domain-extractor writes pure domain unit tests to verify invariants independently.

## Incorrect Behaviors

- **Incorrect:** Vibe-domain-extractor copies database models or controllers directly into the `/domain` folder without removing dependencies.
- **Incorrect:** Vibe-domain-extractor introduces complex dependency injection frameworks or mock frameworks inside pure domain objects.
- **Incorrect:** Vibe-domain-extractor allows unvalidated objects or invalid states to be instantiated inside domain models.
