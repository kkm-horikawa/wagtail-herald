"""
IndexNow notification for instant search engine indexing.
"""

import json
import logging
import threading
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from wagtail.models import Page

logger = logging.getLogger(__name__)

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
INDEXNOW_TIMEOUT_SECONDS = 10


def notify_indexnow(page: Page, api_key: str) -> None:
    """Send IndexNow notification for a published page in a background thread.

    Runs the HTTP request in a daemon thread so the signal handler
    does not block the request/response cycle.
    """
    if not api_key:
        return

    page_url = page.full_url
    if not page_url:
        return

    thread = threading.Thread(
        target=_send_indexnow, args=(page_url, api_key), daemon=True
    )
    thread.start()


def _send_indexnow(page_url: str, api_key: str) -> None:
    """Send the IndexNow HTTP request (runs in background thread)."""
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
