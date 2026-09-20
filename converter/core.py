import re


def convert_surge_to_shadowrocket(content: str) -> str:
    lines = content.split('\n')
    converted_lines = []

    in_script_section = False
    in_url_rewrite_section = False

    for line in lines:
        if not line.strip():
            converted_lines.append(line)
            continue

        if '[Script]' in line:
            in_script_section = True
            in_url_rewrite_section = False
            converted_lines.append(line)
            continue

        if '[Map Local]' in line:
            in_url_rewrite_section = True
            in_script_section = False
            converted_lines.append('[URL Rewrite]')
            continue

        if '[URL Rewrite]' in line:
            in_url_rewrite_section = True
            in_script_section = False
            converted_lines.append(line)
            continue

        if line.startswith('[') and ']' in line:
            in_script_section = False
            in_url_rewrite_section = False
            converted_lines.append(line)
            continue

        if in_script_section and '=' in line and re.search(r'type\s*=|pattern\s*=', line):
            line = re.sub(r'\s*=\s*', '=', line)
            line = re.sub(r',\s+', ',', line)
            converted_lines.append(line)
            continue

        if in_url_rewrite_section and re.match(r'^\^https\?://', line.strip()):
            pattern = line.split()[0]
            converted_lines.append(f"{pattern} - reject-dict")
            continue

        converted_lines.append(line)

    return '\n'.join(converted_lines)
