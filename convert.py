#!/usr/bin/env python3
"""
Surge to Shadowrocket Module Converter
Converts fmz200's Surge modules to Shadowrocket format
"""

import os
import re
import requests
import shutil
from pathlib import Path
import json


def fetch_github_directory(owner, repo, path, ref='main'):
    """Fetch directory contents from GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch directory: {url}")
        return None


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
            # Check if it's a simple pattern without complex parameters
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


def convert_surge_to_shadowrocket(surge_content, module_name=None):
    """Convert Surge module content to Shadowrocket format"""
    # Apply cleaning and conversion
    converted = clean_module_content(surge_content)
    
    # Additional transformations specific to Shadowrocket
    # Replace Map Local section with URL Rewrite
    converted = re.sub(r'\[Map Local\]', '[URL Rewrite]', converted)
    
    return converted


def main():
    print("Starting Surge to Shadowrocket conversion...")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Fetch all parts from fmz200/wool_scripts
    base_parts = ['partA', 'partB', 'partC', 'partD', 'partE', 'partF', 'partG', 
                  'partH', 'partI', 'partJ', 'partK', 'partL', 'partM', 'partN', 
                  'partO', 'partP', 'partQ', 'partR', 'partS', 'partT', 'partU', 
                  'partV', 'partW', 'partX', 'partY', 'partZ']
    
    owner = "fmz200"
    repo = "wool_scripts"
    
    for part in base_parts:
        print(f"Processing {part}...")
        
        # Fetch directory contents
        dir_contents = fetch_github_directory(owner, repo, f"Surge/module/split/{part}")
        
        if not dir_contents:
            print(f"No content found for {part}, skipping...")
            continue
            
        # Process each .sgmodule file in the part
        for item in dir_contents:
            if item['type'] == 'file' and item['name'].endswith('.sgmodule'):
                print(f"Converting {item['name']}...")
                
                # Download the file content
                response = requests.get(item['download_url'])
                if response.status_code == 200:
                    surge_content = response.text
                    
                    # Convert the content
                    shadowrocket_content = convert_surge_to_shadowrocket(surge_content, item['name'])
                    
                    # Write to output directory
                    output_file = output_dir / f"{item['name'].replace('.sgmodule', '.module')}"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(shadowrocket_content)
                    
                    print(f"  ✓ Converted {item['name']} -> {output_file.name}")
                else:
                    print(f"  ✗ Failed to download {item['name']}")
    
    # Also process the main modules
    main_modules = ['weibo.module', 'blockAds.module', 'cookies.module', 'blockHTTPDNS.module']
    
    for module in main_modules:
        print(f"Processing main module {module}...")
        
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/Surge/module/{module}"
        response = requests.get(url)
        
        if response.status_code == 200:
            surge_content = response.text
            shadowrocket_content = convert_surge_to_shadowrocket(surge_content, module)
            
            output_file = output_dir / f"{module.replace('.sgmodule', '.module').replace('.module', '.module')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(shadowrocket_content)
                
            print(f"  ✓ Converted {module} -> {output_file.name}")
        else:
            print(f"  ✗ Failed to download {module}")
    
    print("\nConversion completed!")
    print(f"Output files are in: {output_dir.absolute()}")


if __name__ == "__main__":
    main()