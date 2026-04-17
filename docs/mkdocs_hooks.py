import re

from pathlib import Path


def python_indent(content):
    # Pattern: classic markdown indent (2 spaces) to Python-Markdown indent (4 spaces)
    return re.sub(r'^(\ \ -\ .*)', r'  \1', content, flags=re.MULTILINE)


def on_page_markdown(markdown, page, config, files):
    if page.file.src_path == 'index.md':
        readme_path = Path(Path(config['config_file_path']).parent, 'README.md')
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Rewrite links: [label](docs/...) -> [label](...)
            # This handles both markdown links [text](url) and images ![text](url)
            # We match (docs/ and replace with (

            # Pattern: parenthesis, docs/, everything else
            content = content.replace('](docs/', '](')
            content = content.replace('CONTRIBUTING.md', 'contributing.md')
            content = content.replace('CODE_OF_CONDUCT.md', 'code_of_conduct.md')

            content = python_indent(content)

            return content
        except Exception as e:
            print(f"Error including README.md: {e}")
            return markdown

    # # This is not functional yet:
    # if page.file.src_path == 'contributing.md':
    #     print(markdown)
    #     repo_url = config.get('repo_url', '').rstrip('/')
    #     markdown = markdown.replace(
    #         '](CHANGELOG.md)',
    #         f']({repo_url}/blob/develop/CHANGELOG.md)'
    #     )
    #     markdown = markdown.replace('](/docs/)', '](index.md)')
    #     markdown = markdown.replace('](/docs/ADRs/)', '](adr/index.md)')

    markdown = python_indent(markdown)
    return markdown
