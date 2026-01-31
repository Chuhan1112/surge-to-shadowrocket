#!/usr/bin/env python3
"""
Simple Surge to Shadowrocket Converter
Converts specific modules from fmz200 to test the concept
"""

import requests
import re
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
    print("Converting key Surge modules to Shadowrocket format...")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Define key modules to convert
    modules_to_convert = [
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partX/Xiaohongshu.sgmodule", "Xiaohongshu.module"),
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partT/Twitter.sgmodule", "Twitter.module"), 
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partW/WeChat.sgmodule", "WeChat.module"),
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module", "blockAds.module"),
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/weibo.module", "Weibo.module")
    ]
    
    for url, filename in modules_to_convert:
        print(f"Converting {filename}...")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                surge_content = response.text
                shadowrocket_content = convert_surge_to_shadowrocket(surge_content)
                
                output_file = output_dir / filename
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(shadowrocket_content)
                
                print(f"  ✓ Converted {filename}")
            else:
                print(f"  ✗ Failed to download {filename} (status: {response.status_code})")
        except Exception as e:
            print(f"  ✗ Error converting {filename}: {e}")
    
    # Also convert a few more from different parts
    additional_modules = [
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partB/Bilibili.sgmodule", "Bilibili.module"),
        ("https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partA/Aliexpress.sgmodule", "Aliexpress.module")
    ]
    
    for url, filename in additional_modules:
        print(f"Converting {filename}...")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                surge_content = response.text
                shadowrocket_content = convert_surge_to_shadowrocket(surge_content)
                
                output_file = output_dir / filename
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(shadowrocket_content)
                
                print(f"  ✓ Converted {filename}")
            else:
                print(f"  ✗ Failed to download {filename} (status: {response.status_code})")
        except Exception as e:
            print(f"  ✗ Error converting {filename}: {e}")
    
    print(f"\nConversion completed! Files saved to: {output_dir.absolute()}")
    
    # List all created files
    print("\nCreated files:")
    for file in sorted(output_dir.glob("*.module")):
        size = file.stat().st_size
        print(f"  - {file.name} ({size} bytes)")


if __name__ == "__main__":
    main()