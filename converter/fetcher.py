import time
import logging
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)


def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    delay: float = 1.0,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (content, None) on success.
    Returns (None, "not_found") on 404.
    Returns (None, "request_error") after all retries exhausted.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text, None
            elif response.status_code == 404:
                logger.warning("Module not found (404): %s", url)
                return None, "not_found"
            else:
                logger.warning("Attempt %d failed for %s: HTTP %d", attempt + 1, url, response.status_code)
        except requests.exceptions.RequestException as e:
            logger.warning("Attempt %d failed for %s: %s", attempt + 1, url, e)

        if attempt < max_retries - 1:
            time.sleep(delay * (2 ** attempt))

    logger.error("All %d attempts failed for %s", max_retries, url)
    return None, "request_error"
