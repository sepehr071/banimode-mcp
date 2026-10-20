import json

import pytest

from banimode_mcp.server import compact


@pytest.mark.anyio
async def test_compact_is_single_minified_utf8_json():
    async def tool():
        return {"title": "مانتو", "n": [1, 2]}

    assert await compact(tool)() == '{"title":"مانتو","n":[1,2]}'


@pytest.mark.anyio
async def test_client_gets_one_text_block_and_no_output_schema(api):
    from mcp import Client
    from mcp.types import TextContent

    from banimode_mcp.server import mcp

    api["v4/products/flash-sales-new"] = {"data": {"data": [], "meta": {"total": 0, "current_page": 1, "last_page": 1}}}
    async with Client(mcp) as c:
        result = await c.call_tool("bm_deals", {})
        tools = (await c.list_tools()).tools
    assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
    assert result.structured_content is None
    assert all(t.output_schema is None for t in tools)
    names = sorted(t.name for t in tools)
    assert names == ["bm_brands", "bm_browse", "bm_categories", "bm_deals", "bm_product", "bm_reviews", "bm_search"]
    assert '"title":"' not in json.dumps(tools[0].input_schema)
