"""
IndexNow notification for instant search engine indexing.
"""

import json
import logging
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from wagtail.models import Page

logger = logging.getLogger(__name__)

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
INDEXNOW_TIMEOUT_SECONDS = 10


def notify_indexnow(page: Page, api_key: str) -> None:
    """Send IndexNow notification for a published page."""
    if not api_key:
        return

    page_url = page.full_url
    if not page_url:
        return

    host = urlparse(page_url).netloc

    payload = json.dumps(
        {
            "host": host,
            "key": api_key,
            "keyLocation": f"https://{host}/{api_key}.txt",
            "urlList": [page_url],
        }
    ).encode()

    req = Request(
        INDEXNOW_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        resp = urlopen(req, timeout=INDEXNOW_TIMEOUT_SECONDS)
        logger.info("IndexNow: notified %s (status %s)", page_url, resp.status)
    except URLError as e:
        logger.warning("IndexNow: failed to notify %s: %s", page_url, e)
    except OSError as e:
        logger.warning("IndexNow: unexpected error for %s: %s", page_url, e)
