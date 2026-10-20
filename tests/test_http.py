import httpx
import pytest

from banimode_mcp import http

pytestmark = pytest.mark.anyio


async def test_retries_5xx_then_succeeds():
    n = 0

    def handler(request):
        nonlocal n
        n += 1
        return httpx.Response(503) if n < 3 else httpx.Response(200, json={"status": "success", "data": 1})

    http.set_transport(httpx.MockTransport(handler))
    assert (await http.api("x"))["data"] == 1 and n == 3


async def test_gives_up_after_retries_and_reports_status():
    http.set_transport(httpx.MockTransport(lambda r: httpx.Response(500)))
    with pytest.raises(http.ApiError, match="server error") as e:
        await http.api("x")
    assert e.value.status == 500


async def test_validation_error_message_is_surfaced():
    body = {"status": "error", "message": "page size too big", "data": {}}
    http.set_transport(httpx.MockTransport(lambda r: httpx.Response(422, json=body)))
    with pytest.raises(http.ApiError, match="page size too big"):
        await http.api("v4/products/")


async def test_error_status_in_200_body_raises():
    http.set_transport(httpx.MockTransport(lambda r: httpx.Response(200, json={"status": "error", "message": "bad"})))
    with pytest.raises(http.ApiError, match="bad"):
        await http.api("x")


async def test_connect_error_is_a_tool_error():
    def boom(request):
        raise httpx.ConnectError("no route")

    http.set_transport(httpx.MockTransport(boom))
    with pytest.raises(http.ApiError, match="Could not reach"):
        await http.api("x")


async def test_cached_reuses_value():
    calls = []

    async def make():
        calls.append(1)
        return 7

    assert await http.cached("k", 60, make) == 7 and await http.cached("k", 60, make) == 7 and len(calls) == 1
