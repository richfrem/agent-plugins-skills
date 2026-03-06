# Acceptance Criteria: Plugin Replicator

The plugin-replicator skill must meet the following criteria to be considered operational:

## 1. Discovery Gate
- [ ] The agent NEVER generates a replication command without first asking for source path, destination path, mode (additive/clean/link), and dry-run preference.
- [ ] The agent presents a Recap-Before-Execute summary before generating any commands.

## 2. Bidirectional Awareness
- [ ] The agent correctly interprets push requests ("replicate X to Y") and pull requests ("pull X from agent-plugins-skills into this project").
- [ ] The agent sets --source and --dest correctly for both directions without prompting.

## 3. Dry-Run First
- [ ] For any first-time or clean-mode replication, the agent recommends a --dry-run pass before the live run.
- [ ] The agent waits for explicit confirmation ('yes', 'looks good', 'proceed') before generating the live command.

## 4. Error Handling
- [ ] If source does not exist, agent reports and lists available options. Does NOT retry automatically.
- [ ] If destination does not exist, agent confirms with the user rather than silently creating directories.
- [ ] If --link fails, agent explains the cause and offers to fall back to copy mode.

## 5. Post-Replication Guidance
- [ ] After a successful replication, the agent reminds the user to run `plugin-maintenance sync` in the target project to activate the plugins in agent environments.
