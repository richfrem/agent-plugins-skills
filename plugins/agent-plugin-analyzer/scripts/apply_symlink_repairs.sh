#!/bin/bash
echo 'Repairing symlinks...'
ln -f -s '../SKILL.md' 'plugins/agent-scaffolders/skills/create-command/references/examples/SKILL.md'
ln -f -s '../../../references/post-run-survey.md' 'plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/references/post-run-survey.md'
ln -f -s '../../../references/acceptance-criteria.md' 'plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/acceptance-criteria.md'