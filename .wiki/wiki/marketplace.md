---
concept: marketplace
source: plugin-code
source_file: agent-scaffolders/references/examples/marketplace.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.251360+00:00
cluster: source
content_hash: 326c1ec678a6829b
---

# Marketplace

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/references/examples/marketplace.json -->
{
  "name": "acme-corp-developer-tooling",
  "owner": {
    "name": "Acme Corp"
  },
  "plugins": [
    {
      "name": "internal-db-helper",
      "source": "./plugins/internal-db-helper",
      "strict": true,
      "category": "Data",
      "tags": ["sql", "helper"]
    },
    {
      "name": "slack-bot-connector",
      "source": {
        "source": "github",
        "repo": "acme-corp/slack-bot",
        "ref": "main"
      },
      "strict": false,
      "category": "Integrations"
    }
  ]
}


<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/manage-marketplace/examples/marketplace.json -->
{
  "name": "acme-corp-developer-tooling",
  "owner": {
    "name": "Acme Corp"
  },
  "plugins": [
    {
      "name": "internal-db-helper",
      "source": "./plugins/internal-db-helper",
      "strict": true,
      "category": "Data",
      "tags": ["sql", "helper"]
    },
    {
      "name": "slack-bot-connector",
      "source": {
        "source": "github",
        "repo": "acme-corp/slack-bot",
        "ref": "main"
      },
      "strict": false,
      "category": "Integrations"
    }
  ]
}


## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/references/examples/marketplace.json`
- **Indexed:** 2026-04-27T05:21:04.251360+00:00
