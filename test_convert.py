#!/usr/bin/env python3
"""
Test script to convert a single Surge module to Shadowrocket format
"""

import requests
import re
from pathlib import Path


def clean_module_content(content):
    """Clean and convert Surge module content to Shadowrocket format"""
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
        elif '[Map Local]' in line:
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
            # From: name = type=http-response, pattern=..., script-path=...
            # To: name=type=http-response,pattern=...,script-path=...
            line = re.sub(r'\s*=\s*', '=', line)  # Remove spaces around =
            line = re.sub(r',\s+', ',', line)     # Remove spaces after commas
            converted_lines.append(line)
            continue
            
        # Convert Map Local lines to URL Rewrite reject format
        if in_map_local_section and line.strip().startswith('^https?:\/\/'):
            # Convert Map Local patterns to URL Rewrite reject format
            parts = line.split(' ', 2)
            if len(parts) >= 2:
                pattern = parts[0]
                # Convert to Shadowrocket URL Rewrite reject format
                converted_line = f"{pattern} - reject-dict"
                converted_lines.append(converted_line)
                continue
        
        # Other lines remain the same
        converted_lines.append(line)
    
    return '\n'.join(converted_lines)


def convert_surge_to_shadowrocket(surge_content, module_name=None):
    """Convert Surge module content to Shadowrocket format"""
    # Apply cleaning and conversion
    converted = clean_module_content(surge_content)
    
    # Additional transformations specific to Shadowrocket
    # Replace Map Local section with URL Rewrite
    converted = re.sub(r'\[Map Local\]', '[URL Rewrite]', converted)
    
    return converted


def test_conversion():
    print("Testing conversion with Xiaohongshu module...")
    
    # Download the Xiaohongshu module
    url = "https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partX/Xiaohongshu.sgmodule"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to download module: {response.status_code}")
        return
    
    surge_content = response.text
    print("Original content (first 20 lines):")
    print('\n'.join(surge_content.split('\n')[:20]))
    print("\n" + "="*50 + "\n")
    
    # Convert the content
    shadowrocket_content = convert_surge_to_shadowrocket(surge_content, "Xiaohongshu.sgmodule")
    print("Converted content (first 20 lines):")
    print('\n'.join(shadowrocket_content.split('\n')[:20]))
    
    # Save to output
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "Xiaohongshu.module"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(shadowrocket_content)
    
    print(f"\n✓ Converted module saved to: {output_file.absolute()}")
    
    # Show differences in key sections
    print("\nKey differences:")
    print("- [Map Local] -> [URL Rewrite]")
    print("- Script section formatting (spaces around = removed)")
    print("- Map Local patterns converted to reject-dict format")


if __name__ == "__main__":
    test_conversion()