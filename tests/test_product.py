import pytest
from conftest import fixture

pytestmark = pytest.mark.anyio


async def test_bm_product(client, api):
    api["v4/products/270643"] = fixture("product.json")
    out = (await client.call_tool("bm_product", {"product_id": 270643})).structured_content
    assert out["brand"] == "تولیکا" and out["category"][-1] == "مانتو کوتاه" and out["category_id"]
    assert {"استایل": "Fit (متناسب)"} in out["features"] and "<" not in out["description"]
    c = out["colors"][0]
    assert c["color"] == "کرم" and c["price"] == 599800 and c["final_price"] == 179940 and c["discount_pct"] == 70
    assert c["discount_until"] == "2026-10-20 23:59:59"
    assert c["sizes"] == [{"size": "42", "qty": 1}] and c["sold_out_sizes"] == ["38", "40", "44", "46"]
    assert out["url"].startswith("https://www.banimode.com/BM-270643")


async def test_bm_product_unknown_id(client, api):
    api["v4/products/99999999"] = fixture("empty_product.json")
    result = await client.call_tool("bm_product", {"product_id": 99999999})
    assert result.is_error and "not found" in result.content[0].text


async def test_bm_reviews(client, api):
    api["v2/products/30490/comments"] = fixture("comments.json")
    out = (await client.call_tool("bm_reviews", {"product_id": 30490, "page": 2})).structured_content
    assert out["total"] == 40 and out["pages"] == 4 and len(out["reviews"]) == 3
    first = out["reviews"][0]
    assert first["stars"] == 3 and first["date"] == "2025-10-09" and first["buyer"] is True
    assert "stars" not in out["reviews"][1]  # grade 0 = text only
    assert api.params()["page"] == "2"
