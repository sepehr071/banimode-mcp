"""Shared async HTTP client for the Banimode mobile API (mobapi.banimode.com).

Every tool goes through `api`, which caps concurrency, retries timeouts, dropped connections, 429 and 5xx with
jittered backoff, and turns HTTP failures into `ToolError` messages the model can act on. The API is open JSON (no
login, no cookies); the wire format is a Chrome impersonation (curl_cffi) like the other shop servers.
"""

from __future__ import annotations

import asyncio
import os
import random
import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from httpx_curl_cffi import AsyncCurlTransport
from mcp.server.mcpserver.exceptions import ToolError

SITE = "https://www.banimode.com"
BASE = "https://mobapi.banimode.com/api"

# User-Agent and TLS come from the impersonated Chrome profile (see _get_client).
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    "Origin": SITE,
    "Referer": f"{SITE}/",
}

MAX_CONCURRENCY = 2
JITTER = (0.1, 0.4)  # seconds before each upstream call
MAX_RETRIES = 2
MAX_RETRY_WAIT = 10  # cap for Retry-After and backoff, seconds
RETRY_DELAY = 0.5

_transport: httpx.AsyncBaseTransport | None = None
_client: httpx.AsyncClient | None = None
_limit: asyncio.Semaphore | None = None
_proxy_index = 0
_cache: dict[Any, tuple[float, Any]] = {}


class ApiError(ToolError):
    """A failed upstream call. `status` is the HTTP status, or None for network errors."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def set_transport(transport: httpx.AsyncBaseTransport | None) -> None:
    """Swap the transport (tests use httpx.MockTransport). Drops the current client and the cache."""
    global _transport, _client, _limit, _proxy_index
    _transport, _client, _limit, _proxy_index = transport, None, None, 0
    _cache.clear()


async def cached(key: Any, ttl: float, make: Callable[[], Awaitable[Any]]) -> Any:
    """Return make()'s result, reused for `ttl` seconds per key. Only for results nobody mutates."""
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < ttl:
        return hit[1]
    value = await make()
    _cache[key] = (time.monotonic(), value)
    return value


def _proxies() -> list[str]:
    """BANIMODE_MCP_PROXY: one proxy URL, or a comma-separated list used one at a time."""
    return [p.strip() for p in os.environ.get("BANIMODE_MCP_PROXY", "").split(",") if p.strip()]


def _get_client() -> tuple[httpx.AsyncClient, asyncio.Semaphore]:
    global _client, _limit
    if _client is None:
        # Direct connections work from Iran and abroad; a proxy is only used when the user opts in.
        proxies = _proxies()
        _client = httpx.AsyncClient(
            transport=_transport
            or AsyncCurlTransport(
                impersonate="chrome",
                default_headers=True,
                proxy=proxies[_proxy_index % len(proxies)] if proxies else None,
                max_connections=2 * MAX_CONCURRENCY,
            ),
            headers=HEADERS,
            timeout=30,
            limits=httpx.Limits(max_connections=2 * MAX_CONCURRENCY),
            follow_redirects=True,
            trust_env=False,
        )
        _limit = asyncio.Semaphore(MAX_CONCURRENCY)
    assert _limit is not None
    return _client, _limit


async def api(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET <BASE>/<path>; returns the parsed body (`{"status", "message", "data", ...}`)."""
    global _client, _limit, _proxy_index
    retries = 0
    while True:
        client, limit = _get_client()
        wait = None
        try:
            async with limit:
                await asyncio.sleep(random.uniform(*JITTER))
                r = await client.get(f"{BASE}/{path}", params=params)
        except httpx.TimeoutException as e:
            err = ApiError("mobapi.banimode.com did not answer in time. Try again in a moment.")
            err.__cause__ = e
        except httpx.TransportError as e:
            if len(_proxies()) > 1 and client is _client:  # rotate the proxy list after a connect failure
                _client, _limit, _proxy_index = None, None, _proxy_index + 1
            err = ApiError(
                f"Could not reach mobapi.banimode.com ({type(e).__name__}). Check the internet connection, "
                "or set BANIMODE_MCP_PROXY."
            )
            err.__cause__ = e
        else:
            if r.status_code == 429 or r.status_code >= 500:
                err = ApiError(_status_message(r), r.status_code)
                v = r.headers.get("retry-after", "")
                wait = float(v) if v.replace(".", "", 1).isdigit() else None
            elif r.status_code >= 400:
                raise ApiError(_status_message(r), r.status_code)
            else:
                try:
                    body = r.json()
                except ValueError as e:
                    raise ApiError(f"mobapi.banimode.com returned a non-JSON response for {path}.") from e
                if isinstance(body, dict) and body.get("status") == "error":
                    raise ApiError(f"mobapi.banimode.com error for {path}: {str(body.get('message'))[:200]}")
                return body
        if retries == MAX_RETRIES:
            raise err
        wait = wait if wait is not None else RETRY_DELAY * 2**retries * random.uniform(1, 1.5)
        retries += 1
        await asyncio.sleep(min(wait, MAX_RETRY_WAIT))


def _status_message(r: httpx.Response) -> str:
    code = r.status_code
    if code == 403:
        return "mobapi.banimode.com blocked the request (HTTP 403). Turn off VPN/proxy or set BANIMODE_MCP_PROXY."
    if code == 404:
        return "Not found on mobapi.banimode.com (HTTP 404)."
    if code == 429:
        return "mobapi.banimode.com is rate limiting requests (HTTP 429). Wait a minute before retrying."
    if code >= 500:
        return f"mobapi.banimode.com had a server error (HTTP {code}). Try again later."
    try:  # validation errors: {"status": "error", "message": "..."}
        detail = r.json().get("message")
    except (ValueError, AttributeError):
        detail = None
    return f"mobapi.banimode.com rejected the request (HTTP {code}){': ' + str(detail)[:300] if detail else '.'}"
