# Acceptance Criteria: Vector DB Launch

These test metrics evaluate the initial startup flow for the podman-based external Vector database architecture.

### Scenario: Launching the Database Containers
**Given** a properly configured `.env` file referencing a host and port
**When** the user executes the `vector-db-launch` skill
**Then** the agent should guide the user through starting the external podman containers via `make up` or standard container commands
**And** the agent should confirm port 8110 is active and responding.
