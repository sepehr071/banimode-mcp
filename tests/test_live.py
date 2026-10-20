import pytest

pytestmark = [pytest.mark.anyio, pytest.mark.live]


async def call(client, name, args):
    result = await client.call_tool(name, args)
    assert not result.is_error, result.content[0].text
    return result.structured_content


async def test_bm_search(client):
    data = await call(client, "bm_search", {"query": "مانتو", "sort": "cheapest", "limit": 10, "size": "M"})
    assert data["total"] > 50 and len(data["products"]) == 10
    prices = [p["final_price"] for p in data["products"]]
    assert prices == sorted(prices) and prices[0] > 1000


async def test_bm_search_price_range(client):
    data = await call(client, "bm_search", {"query": "کفش", "min_price": 500000, "max_price": 900000, "limit": 20})
    assert data["products"] and all(500000 <= p["final_price"] <= 900000 for p in data["products"])


async def test_bm_browse_and_lookups(client):
    cats = await call(client, "bm_categories", {"query": "مانتو"})
    assert cats["categories"]
    data = await call(client, "bm_browse", {"category_id": cats["categories"][0]["id"], "limit": 5})
    assert data["total"] > 10 and data["products"]
    brands = await call(client, "bm_brands", {"query": "ایکات"})
    assert any(b["en_name"] == "Ecut" for b in brands["brands"])
    data = await call(client, "bm_browse", {"brand_id": brands["brands"][0]["id"], "limit": 5})
    assert data["products"]
    kids = await call(client, "bm_categories", {"parent_id": 4})
    assert kids["categories"]


async def test_bm_deals(client):
    data = await call(client, "bm_deals", {"limit": 10})
    assert data["total"] > 0 and data["products"] and all(p.get("discount_pct") for p in data["products"])


async def test_bm_product_and_reviews(client):
    hit = (await call(client, "bm_search", {"query": "مانتو", "limit": 5}))["products"][0]
    p = await call(client, "bm_product", {"product_id": hit["id"]})
    assert p["title"] and p["colors"] and p["colors"][0]["final_price"] > 1000
    r = await call(client, "bm_reviews", {"product_id": 30490})
    assert r["total"] > 0 and r["reviews"] and r["reviews"][0]["text"]
