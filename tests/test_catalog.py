import httpx
import pytest
from conftest import fixture

pytestmark = pytest.mark.anyio


async def test_bm_search_cards_and_params(client, api):
    api["v4/products/"] = fixture("search.json")
    out = (
        await client.call_tool(
            "bm_search", {"query": "مانتو", "sort": "cheapest", "min_price": 100000, "max_price": 300000, "limit": 3}
        )
    ).structured_content
    assert out["total"] == 328 and out["page"] == 1 and out["pages"] == 110 and len(out["products"]) == 3
    p = out["products"][0]
    assert p["id"] and p["title"] and p["final_price"] > 0 and p["url"].startswith("https://www.banimode.com/BM-")
    assert all(v is not None for v in p.values())
    q = api.params()
    assert q["q"] == "مانتو" and q["page_size"] == "3" and q["filter[total_qty][gt]"] == "0"
    assert q["sort[asc]"] == "price"
    # Toman -> Rial for the API
    assert q["filter[product_final_price][gte]"] == "1000000" and q["filter[product_final_price][lte]"] == "3000000"


async def test_card_prices_are_toman_with_discount():
    from banimode_mcp.catalog import card

    c = card(fixture("flash.json")["data"]["data"][0])
    assert c["price"] == 599800 and c["final_price"] == 179940 and c["discount_pct"] == 70
    assert c["sizes"] == ["42"] and c["url"].startswith("https://www.banimode.com/BM-")
    assert c["url"] == "https://www.banimode.com/BM-270643"


async def test_bm_search_options_off(client, api):
    api["v4/products/"] = fixture("search.json")
    await client.call_tool("bm_search", {"query": "مانتو", "in_stock": False, "category_id": 668, "brand_id": 305})
    q = api.params()
    assert "filter[total_qty][gt]" not in q and not any(k.startswith("sort") for k in q)
    assert q["filter[product_categories.id][eq]"] == "668" and q["filter[product_manufacturer_id][eq]"] == "305"


async def test_bm_search_size_resolves_to_id(client, api):
    def route(request):
        body = fixture("facets.json") if "need_filter" in request.url.params else fixture("search.json")
        return httpx.Response(200, json=body)

    api["v4/products/"] = route
    sizes = fixture("facets.json")["data"]["filters"]["sizes"]
    await client.call_tool("bm_search", {"query": "مانتو", "size": sizes[2]["name"].lower()})
    assert api.params()["filter[available_sizes][in]"] == str(sizes[2]["id"])
    result = await client.call_tool("bm_search", {"query": "مانتو", "size": "nonsense"})
    assert result.is_error and "Unknown size" in result.content[0].text


async def test_bm_browse_needs_a_filter(client, api):
    result = await client.call_tool("bm_browse", {})
    assert result.is_error and "category_id" in result.content[0].text
    api["v4/products/"] = fixture("search.json")
    out = (await client.call_tool("bm_browse", {"category_id": 11, "sort": "discount"})).structured_content
    assert out["products"] and api.params()["sort[desc]"] == "discount"


async def test_bm_categories(client, api):
    api["v4/products/"] = fixture("facets.json")
    top = (await client.call_tool("bm_categories", {})).structured_content
    assert top["total"] == 2 and all(c["level"] == 2 for c in top["categories"])
    first = top["categories"][0]
    kids = (await client.call_tool("bm_categories", {"parent_id": first["id"]})).structured_content
    assert kids["categories"] and all(c["parent"] == first["name"] for c in kids["categories"])
    hit = (await client.call_tool("bm_categories", {"query": kids["categories"][0]["name"]})).structured_content
    assert hit["categories"][0]["id"] == kids["categories"][0]["id"]
    assert len(api.calls) == 1  # facets are cached


async def test_bm_brands(client, api):
    api["v4/products/"] = fixture("facets.json")
    brands = fixture("facets.json")["data"]["filters"]["manufacturers"]
    out = (await client.call_tool("bm_brands", {"query": brands[1]["name"]})).structured_content
    assert out["brands"][0]["id"] == brands[1]["id"]
    out = (await client.call_tool("bm_brands", {"query": brands[1]["en_name"].upper()})).structured_content
    assert out["brands"][0]["id"] == brands[1]["id"]


async def test_bm_deals(client, api):
    api["v4/products/flash-sales-new"] = fixture("flash.json")
    out = (await client.call_tool("bm_deals", {"limit": 2})).structured_content
    assert out["total"] == 639 and len(out["products"]) == 2 and out["ends_in_minutes"] > 0
    assert out["products"][0]["discount_pct"] == 70 and api.params()["page"] == "1"
