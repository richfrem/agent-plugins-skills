import os
import re

def purge_installation_sections(root_dir):
    plugins_dir = os.path.join(root_dir, 'plugins')
    if not os.path.isdir(plugins_dir):
        print(f"Plugins directory not found at {plugins_dir}")
        return

    # Pattern to match ## Installation until the next ## header
    # Using re.DOTALL to match across multiple lines
    install_pattern = re.compile(r'^## Installation.*?^(?=\s*## )', re.MULTILINE | re.DOTALL)

    for plugin_name in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, plugin_name)
        if not os.path.isdir(plugin_path):
            continue

        readme_path = os.path.join(plugin_path, 'README.md')
        if os.path.exists(readme_path):
            print(f"Processing {readme_path}...")
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove the Installation section
            new_content = install_pattern.sub('', content)

            # Clean up potential triple newlines at the end of the removed section
            new_content = re.sub(r'\n{3,}', '\n\n', new_content)

            if content != new_content:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  Successfully purged installation section from {plugin_name}/README.md")
            else:
                print(f"  No installation section found or already purged in {plugin_name}/README.md")

if __name__ == "__main__":
    purge_installation_sections(os.getcwd())
