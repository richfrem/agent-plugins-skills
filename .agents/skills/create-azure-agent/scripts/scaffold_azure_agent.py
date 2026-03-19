#!/usr/bin/env python3
"""
scaffold_azure_agent.py

Generates Azure AI Foundry Agent boilerplate from an existing Open Skill.
Outputs:
  - azure_agent.py (Python SDK Orchestrator)
  - main.bicep (Basic Infrastructure)
"""

import os
import sys
import argparse
from pathlib import Path

PYTHON_TEMPLATE = '''"""
Azure AI Foundry Agent Integration
==================================

This script instantiates the {skill_name} Agent using the Azure AI Projects SDK.
It maps the authoritative SKILL.md into the agent's instructions payload.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

def deploy_agent():
    # 1. Initialize Client
    connection_string = os.environ.get("PROJECT_CONNECTION_STRING")
    if not connection_string:
        print("Set PROJECT_CONNECTION_STRING environment variable.")
        return

    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=connection_string,
    )

    # 2. Read Authoritative Open Skill
    skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            skill_instructions = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find SKILL.md at {skill_md_path}")
        return

    # 3. Instantiate Foundry Agent
    print(f"Deploying {skill_name} to Azure Foundry...")
    
    with project_client:
        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="{skill_name}",
            instructions=skill_instructions,
            headers={{"x-ms-enable-preview": "true"}}
        )
        print(f"Created agent, ID: {{agent.id}}")

if __name__ == "__main__":
    deploy_agent()
'''

BICEP_TEMPLATE = '''// Basic Azure AI Foundry Environment
// Requires setting up a Hub, Project, and Model Deployment.

param location string = resourceGroup().location
param projectName string = '{skill_name}-project'

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01-preview' = {{
  name: projectName
  location: location
  kind: 'Project'
  properties: {{
    description: 'Project for {skill_name} Agent'
    // Ensure you link to your Enterprise AI Hub here:
    // hubResourceId: hubResourceId
  }}
}}

output projectConnectionString string = aiProject.properties.workspaceId
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Path to the target skill directory")
    args = parser.parse_args()

    skill_dir = Path(args.skill)
    if not skill_dir.exists() or not (skill_dir / "SKILL.md").exists():
        print(f"Error: Valid SKILL.md not found in {skill_dir}")
        sys.exit(1)

    skill_name = skill_dir.name
    
    output_dir = skill_dir / "azure_deployment"
    output_dir.mkdir(exist_ok=True)

    py_path = output_dir / "azure_agent.py"
    bicep_path = output_dir / "main.bicep"

    py_path.write_text(PYTHON_TEMPLATE.format(skill_name=skill_name), encoding="utf-8")
    bicep_path.write_text(BICEP_TEMPLATE.format(skill_name=skill_name), encoding="utf-8")

    print(f"Successfully scaffolded Azure Foundry integration for '{skill_name}'.")
    print(f"  -> Generated: {py_path.relative_to(Path.cwd())}")
    print(f"  -> Generated: {bicep_path.relative_to(Path.cwd())}")

if __name__ == "__main__":
    main()
