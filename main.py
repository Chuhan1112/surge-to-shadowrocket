#!/usr/bin/env python3
"""
Surge to Shadowrocket Converter
Usage:
  python main.py                        # selective mode (default, reads config.yaml)
  python main.py --mode bulk            # convert all partA-Z modules from fmz200/wool_scripts
  python main.py --mode selective --output-dir my_output
"""

import argparse
import logging
import sys
from pathlib import Path

import requests

from converter.config import load_config
from converter.core import convert_surge_to_shadowrocket
from converter.fetcher import fetch_with_retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PARTS = [f"part{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]


def run_selective(config: dict, output_dir: Path) -> int:
    github = config.get('github', {})
    owner = github.get('owner', 'fmz200')
    repo = github.get('repo', 'wool_scripts')
    branch = github.get('branch', 'main')

    modules = config.get('modules', [])
    total = len(modules)
    success = fail = skipped = request_errors = 0

    for i, module in enumerate(modules):
        source, output_name = module['source'], module['output']
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{source}"
        logger.info("(%d/%d) Converting %s...", i + 1, total, output_name)

        content, err = fetch_with_retry(url)
        if content is None:
            if err == "not_found":
                logger.warning("  Skipping %s (not found)", output_name)
                skipped += 1
            else:
                logger.error("  Failed to fetch %s", output_name)
                fail += 1
                request_errors += 1
            continue

        converted = convert_surge_to_shadowrocket(content)
        (output_dir / output_name).write_text(converted, encoding='utf-8')
        logger.info("  Converted %s", output_name)
        success += 1

    _log_summary(success, fail, skipped, output_dir)
    return request_errors


def run_bulk(owner: str, repo: str, output_dir: Path) -> int:
    success = fail = skipped = request_errors = 0

    for part in PARTS:
        logger.info("Processing %s...", part)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/Surge/module/split/{part}"
        try:
            resp = requests.get(api_url, timeout=30)
        except requests.exceptions.RequestException as e:
            logger.warning("Failed to list %s: %s", part, e)
            continue

        if resp.status_code == 404:
            continue
        if resp.status_code != 200:
            logger.warning("Failed to list %s: HTTP %d", part, resp.status_code)
            continue

        for item in resp.json():
            if not (item.get('type') == 'file' and item['name'].endswith('.sgmodule')):
                continue

            output_name = item['name'].replace('.sgmodule', '.module')
            content, err = fetch_with_retry(item['download_url'])
            if content is None:
                if err == "not_found":
                    skipped += 1
                else:
                    fail += 1
                    request_errors += 1
                continue

            converted = convert_surge_to_shadowrocket(content)
            (output_dir / output_name).write_text(converted, encoding='utf-8')
            logger.info("  Converted %s", output_name)
            success += 1

    main_modules = ['weibo.module', 'blockAds.module', 'cookies.module', 'blockHTTPDNS.module']
    for module in main_modules:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/Surge/module/{module}"
        content, err = fetch_with_retry(url)
        if content is None:
            skipped += 1 if err == "not_found" else 0
            if err != "not_found":
                fail += 1
                request_errors += 1
            continue
        converted = convert_surge_to_shadowrocket(content)
        (output_dir / module).write_text(converted, encoding='utf-8')
        logger.info("  Converted %s", module)
        success += 1

    _log_summary(success, fail, skipped, output_dir)
    return request_errors


def _log_summary(success: int, fail: int, skipped: int, output_dir: Path) -> None:
    logger.info("Conversion complete — success: %d  failed: %d  skipped: %d", success, fail, skipped)
    logger.info("Output: %s", output_dir.absolute())
    for f in sorted(output_dir.glob("*.module")):
        logger.info("  %s (%d bytes)", f.name, f.stat().st_size)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Surge modules to Shadowrocket format")
    parser.add_argument('--mode', choices=['selective', 'bulk'], default='selective')
    parser.add_argument('--output-dir', default='output')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    if args.mode == 'selective':
        config = load_config(Path('config.yaml'))
        request_errors = run_selective(config, output_dir)
    else:
        request_errors = run_bulk('fmz200', 'wool_scripts', output_dir)

    if request_errors:
        logger.error("Exiting with error due to %d fetch failure(s)", request_errors)
        sys.exit(1)


if __name__ == '__main__':
    main()