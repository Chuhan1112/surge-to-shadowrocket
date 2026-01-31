#!/usr/bin/env python3
"""
Enhanced Surge to Shadowrocket Converter
Uses configuration file to specify which modules to convert
"""

import requests
import re
import yaml
from pathlib import Path


def convert_surge_to_shadowrocket(content):
    """Convert Surge module content to Shadowrocket format"""
    # First, replace [Map Local] with [URL Rewrite]
    content = content.replace('[Map Local]', '[URL Rewrite]')
    
    lines = content.split('\n')
    converted_lines = []
    
    in_script_section = False
    in_map_local_section = False
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            converted_lines.append(line)
            continue
            
        # Handle script section conversions
        if '[Script]' in line:
            in_script_section = True
            converted_lines.append(line)
            continue
        elif '[Map Local]' in line:  # This should not occur anymore after replacement, but kept for safety
            in_map_local_section = True
            # Replace with URL Rewrite
            converted_lines.append('[URL Rewrite]')
            continue
        elif '[URL Rewrite]' in line:
            in_map_local_section = True
            converted_lines.append(line)
            continue
        elif line.startswith('[') and ']' in line:
            in_script_section = False
            in_map_local_section = False
            converted_lines.append(line)
            continue
            
        # Convert script lines (remove spaces and equals before type)
        if in_script_section and '=' in line and ('type=' in line or 'pattern=' in line):
            # Remove spaces around = and convert Surge format to Shadowrocket format
            line = re.sub(r'\s*=\s*', '=', line)  # Remove spaces around =
            line = re.sub(r',\s+', ',', line)     # Remove spaces after commas
            converted_lines.append(line)
            continue
            
        # Convert Map Local lines to URL Rewrite reject format (now they're in URL Rewrite section)
        if in_map_local_section and line.strip().startswith('^https?:\/\/'):
            # Convert Map Local patterns to URL Rewrite reject format
            parts = line.split(' ', 2)
            if len(parts) >= 1:
                pattern = parts[0]
                # Convert to Shadowrocket URL Rewrite reject format
                converted_line = f"{pattern} - reject-dict"
                converted_lines.append(converted_line)
                continue
        
        # Other lines remain the same
        converted_lines.append(line)
    
    return '\n'.join(converted_lines)


def main():
    print("🚀 Starting Surge to Shadowrocket conversion...")
    
    # Load configuration
    config_path = Path("config.yaml")
    if not config_path.exists():
        print(f"❌ Config file {config_path} not found")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    github_info = config.get('github', {})
    owner = github_info.get('owner', 'fmz200')
    repo = github_info.get('repo', 'wool_scripts')
    branch = github_info.get('branch', 'main')
    
    success_count = 0
    fail_count = 0
    
    # Process each module from config
    for module in config.get('modules', []):
        source = module['source']
        output_name = module['output']
        
        print(f"🔄 Converting {output_name}...")
        
        # Build the URL
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{source}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                surge_content = response.text
                shadowrocket_content = convert_surge_to_shadowrocket(surge_content)
                
                output_file = output_dir / output_name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(shadowrocket_content)
                
                print(f"  ✅ Converted {output_name}")
                success_count += 1
            else:
                print(f"  ❌ Failed to download {output_name} (status: {response.status_code})")
                print(f"     URL: {url}")
                fail_count += 1
        except Exception as e:
            print(f"  ❌ Error converting {output_name}: {e}")
            fail_count += 1
    
    print(f"\n🎉 Conversion completed!")
    print(f"   Success: {success_count} modules")
    print(f"   Failed:  {fail_count} modules")
    print(f"   Output:  {output_dir.absolute()}")
    
    # List all created files
    print(f"\n📁 Created files:")
    for file in sorted(output_dir.glob("*.module")):
        size = file.stat().st_size
        print(f"   • {file.name} ({size} bytes)")


if __name__ == "__main__":
    main()