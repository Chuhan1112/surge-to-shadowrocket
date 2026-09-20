import re


def convert_surge_to_shadowrocket(content: str) -> str:
    """
    Convert a Surge .sgmodule to Shadowrocket-compatible format.

    Transformations applied:
    - [Map Local]  : keep section; strip `status-code=N` from rule lines
                     (Shadowrocket supports Map Local but ignores that field)
    - [Rule]       : drop Surge-only compound logic lines (AND,/OR,/NOT,)
    - [Script]     : normalise spacing around = and after commas;
                     remove Surge-only fields (engine=, max-size=);
                     rewrite binary-body-mode=1 → binary-body-mode=true
    - everything else: pass through unchanged
    """
    lines = content.split('\n')
    converted_lines = []

    in_script_section = False
    in_map_local_section = False
    in_rule_section = False

    for line in lines:
        if not line.strip():
            converted_lines.append(line)
            continue

        # ── Section header ──────────────────────────────────────────────
        if line.startswith('[') and ']' in line:
            in_script_section = '[Script]' in line
            in_map_local_section = '[Map Local]' in line
            in_rule_section = '[Rule]' in line
            converted_lines.append(line)
            continue

        # ── [Rule]: drop Surge compound-logic rules ──────────────────────
        if in_rule_section and re.match(r'^(AND|OR|NOT),', line.strip()):
            continue

        # ── [Map Local]: strip status-code field ─────────────────────────
        if in_map_local_section and not line.lstrip().startswith('#'):
            line = re.sub(r'\s+status-code=\d+', '', line)
            converted_lines.append(line)
            continue

        # ── [Script]: normalise format, remove Surge-only fields ─────────
        if in_script_section and '=' in line and re.search(r'type\s*=|pattern\s*=', line):
            line = re.sub(r'\s*=\s*', '=', line)
            line = re.sub(r',\s+', ',', line)
            line = re.sub(r',engine=[^,]+', '', line)
            line = re.sub(r',max-size=[^,]+', '', line)
            line = re.sub(r'\bbinary-body-mode=1\b', 'binary-body-mode=true', line)
            converted_lines.append(line)
            continue

        converted_lines.append(line)

    return '\n'.join(converted_lines)
