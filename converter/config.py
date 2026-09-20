import logging
from pathlib import Path
from typing import Dict

import yaml

logger = logging.getLogger(__name__)


def load_config(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not validate_config(config):
        raise ValueError("Invalid config structure")
    return config


def validate_config(config: Dict) -> bool:
    if not isinstance(config.get('modules'), list):
        logger.error("Config 'modules' must be a list")
        return False
    for i, module in enumerate(config['modules']):
        if not isinstance(module, dict) or 'source' not in module or 'output' not in module:
            logger.error("Module %d missing 'source' or 'output' key", i)
            return False
    return True
