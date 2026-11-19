"""Conservative HTTP client used by the scanner.

Every request is GET-only, scope-checked, size-limited and has short timeouts.
Redirects are followed manually so that off-scope hosts are never contacted.
"""

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit

import requests

from config import Config
from scanners.url_guard import TargetValidationError, normalize_target, resolve_target


@dataclass
class FetchResult:
    url: str
    status_code: int
    headers: dict
    body: str
    set_cookie_headers: list
    elapsed_ms: int = 0
    error: str = ""
    final_url: str = ""
    redirect_chain: list = field(default_factory=list)

    @property
    def ok(self):
        return not self.error


class SafeFetcher:
    def __init__(self, target_info):
        self.target = target_info
        self.host = target_info["host"]
        self.port = target_info["port"]
        self.base_url = target_info["url"]
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "SecureAI-Passive-Scanner/1.0 (authorized assessment)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.8",
                "Connection": "close",
            }
        )

    def _in_scope(self, url):
        try:
            normalized, host, port, _scheme = normalize_target(url)
            resolve_target(host, port)
        except TargetValidationError:
            return False, url
        return (host == self.host and port == self.port), normalized

    def fetch(self, reference, method="GET"):
        if method.upper() != "GET":
            return FetchResult(str(reference), 0, {}, "", [], error="Only GET requests are allowed")
        url = urljoin(self.base_url, str(reference))
        chain = []
        for _ in range(Config.MAX_REDIRECTS + 1):
            allowed, checked_url = self._in_scope(url)
            if not allowed:
                return FetchResult(
                    url, 0, {}, "", [], error="Blocked: target or redirect is outside the authorized scope", redirect_chain=chain
                )
            url = checked_url
            try:
                response = self.session.request(
                    "GET",
                    url,
                    allow_redirects=False,
                    timeout=(Config.SCAN_CONNECT_TIMEOUT, Config.SCAN_READ_TIMEOUT),
                    stream=True,
                )
            except requests.RequestException as exc:
                return FetchResult(url, 0, {}, "", [], error=f"Request failed: {type(exc).__name__}", redirect_chain=chain)

            elapsed = int(response.elapsed.total_seconds() * 1000) if response.elapsed else 0
            content = bytearray()
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    remaining = Config.MAX_RESPONSE_BYTES - len(content)
                    if remaining <= 0:
                        break
                    content.extend(chunk[:remaining])
                    if len(content) >= Config.MAX_RESPONSE_BYTES:
                        break
            except requests.RequestException:
                pass
            finally:
                response.close()

            encoding = response.encoding or response.apparent_encoding or "utf-8"
            try:
                body = bytes(content).decode(encoding, errors="replace")
            except (LookupError, TypeError):
                body = bytes(content).decode("utf-8", errors="replace")

            headers = {str(k).lower(): str(v) for k, v in response.headers.items()}
            cookie_headers = []
            try:
                cookie_headers = list(response.raw.headers.getlist("Set-Cookie"))
            except (AttributeError, TypeError):
                raw_cookie = response.headers.get("Set-Cookie")
                if raw_cookie:
                    cookie_headers = [raw_cookie]

            if response.is_redirect and response.headers.get("Location"):
                location = response.headers["Location"]
                chain.append({"from": url, "to": location, "status": response.status_code})
                url = urljoin(url, location)
                continue

            return FetchResult(
                url=url,
                status_code=response.status_code,
                headers=headers,
                body=body,
                set_cookie_headers=cookie_headers,
                elapsed_ms=elapsed,
                final_url=url,
                redirect_chain=chain,
            )
        return FetchResult(url, 0, {}, "", [], error="Too many redirects", redirect_chain=chain)

    def close(self):
        self.session.close()
