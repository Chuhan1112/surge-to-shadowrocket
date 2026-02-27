#!/usr/bin/env python3
"""
Enhanced Surge to Shadowrocket Converter
Uses configuration file to specify which modules to convert
"""

import requests
import re
import yaml
import time
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_surge_to_shadowrocket(content: str) -> str:
    """
    Convert Surge module content to Shadowrocket format
    
    Args:
        content: Raw Surge module content
        
    Returns:
        Converted Shadowrocket module content
    """
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


def validate_config(config: Dict) -> bool:
    """
    Validate the configuration structure
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ['modules']
    if not all(key in config for key in required_keys):
        logger.error(f"Config missing required keys: {required_keys}")
        return False
    
    if not isinstance(config['modules'], list):
        logger.error("Config 'modules' must be a list")
        return False
    
    for i, module in enumerate(config['modules']):
        if not isinstance(module, dict):
            logger.error(f"Module {i} must be a dictionary")
            return False
        if 'source' not in module or 'output' not in module:
            logger.error(f"Module {i} missing 'source' or 'output' key")
            return False
    
    return True


def fetch_with_retry(url: str, max_retries: int = 3, delay: float = 1.0) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch content with retry logic
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        Tuple of (content, error_type)
        error_type can be:
          - None: success
          - "not_found": 404 returned from source
          - "request_error": network or non-404 HTTP errors
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text, None
            elif response.status_code == 404:
                logger.warning(f"Module not found (404): {url}")
                return None, "not_found"  # Don't retry 404 errors
            else:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    logger.error(f"All {max_retries} attempts failed for {url}")
    return None, "request_error"


def main():
    logger.info("🚀 Starting Surge to Shadowrocket conversion...")
    
    # Load configuration
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.error(f"❌ Config file {config_path} not found")
        return
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"❌ Error parsing config file: {e}")
        return
    except UnicodeDecodeError as e:
        logger.error(f"❌ Error decoding config file: {e}")
        return
    
    # Validate configuration
    if not validate_config(config):
        logger.error("❌ Config validation failed")
        return
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    github_info = config.get('github', {})
    owner = github_info.get('owner', 'fmz200')
    repo = github_info.get('repo', 'wool_scripts')
    branch = github_info.get('branch', 'main')
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    request_error_count = 0
    
    # Process each module from config
    total_modules = len(config.get('modules', []))
    for i, module in enumerate(config.get('modules', [])):
        source = module['source']
        output_name = module['output']
        
        logger.info(f"🔄 Converting ({i+1}/{total_modules}) {output_name}...")
        
        # Build the URL
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{source}"
        
        # Fetch content with retry logic
        surge_content, error_type = fetch_with_retry(url)

        if surge_content is None:
            if error_type == "not_found":
                logger.warning(f"  ⚠️  Skipping {output_name} (not found)")
                skipped_count += 1
            else:
                logger.error(f"  ❌ Failed to fetch {output_name} due to request errors")
                fail_count += 1
                request_error_count += 1
            continue
        
        try:
            shadowrocket_content = convert_surge_to_shadowrocket(surge_content)
            
            output_file = output_dir / output_name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(shadowrocket_content)
            
            logger.info(f"  ✅ Converted {output_name}")
            success_count += 1
        except Exception as e:
            logger.error(f"  ❌ Error converting {output_name}: {e}")
            fail_count += 1
    
    logger.info(f"\n🎉 Conversion completed!")
    logger.info(f"   Success: {success_count} modules")
    logger.info(f"   Failed:  {fail_count} modules")
    logger.info(f"   Skipped: {skipped_count} modules (not found)")
    logger.info(f"   Output:  {output_dir.absolute()}")
    
    # List all created files
    logger.info(f"\n📁 Created files:")
    for file in sorted(output_dir.glob("*.module")):
        size = file.stat().st_size
        logger.info(f"   • {file.name} ({size} bytes)")

    # Fail fast on request errors so GitHub Actions doesn't silently report "No changes"
    if request_error_count > 0:
        logger.error(
            "\n❌ Conversion failed due to source fetch errors. "
            "This usually indicates network/proxy issues or upstream access problems."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
