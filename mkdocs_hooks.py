import os
import re

def on_page_markdown(markdown, page, config, files):
    if page.file.src_path == 'index.md':
        readme_path = os.path.join(os.path.dirname(config['config_file_path']), 'README.md')
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Rewrite links: [label](docs/...) -> [label](...)
            # This handles both markdown links [text](url) and images ![text](url)
            # We match (docs/ and replace with (
            
            # Pattern: parenthesis, docs/, everything else
            content = content.replace('](docs/', '](')
            
            return content
        except Exception as e:
            print(f"Error including README.md: {e}")
            return markdown
    return markdown
