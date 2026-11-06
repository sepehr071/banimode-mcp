"""Search, browse, categories, brands and flash-sale deals (the `products` list API)."""

from __future__ import annotations

import asyncio
from typing import Annotated, Any, Literal

from pydantic import Field

from .http import SITE, ApiError, api, cached
from .registry import tool

# Sort name -> (direction, API field). Only these fields were confirmed to change the order.
SORTS = {
    "cheapest": ("asc", "price"),
    "expensive": ("desc", "price"),
    "discount": ("desc", "discount"),
    "newest": ("desc", "date"),
}
FACET_TTL = 3600
SCAN_PAGES = 8  # sorted search: most pages of 50 read to find rows that really match the words
Sort = Literal["relevance", "cheapest", "expensive", "discount", "newest"]


def toman(rial: Any) -> int:
    """The API prices in Rial; tools speak Toman."""
    return int(rial or 0) // 10


def card(p: dict[str, Any]) -> dict[str, Any]:
    """One listing entry (one product in one color), trimmed. Null/zero fields are left out."""
    base, final = toman(p.get("product_base_price") or p.get("product_price")), toman(p.get("product_final_price"))
    spec = p.get("product_specific_price") or {}
    # the spec percent can be stale (flash sales showed 5 for 22,000 -> 17,600), so trust the prices
    pct = round(100 - 100 * final / base) if base > final else spec.get("discount_percent")
    out = {
        "id": p["id_product"],
        "title": p["product_name"],
        "brand": p.get("product_manufacturer_name"),
        "color": p.get("color_name"),
        "price": base if base > final else None,
        "final_price": final,
        "discount_pct": pct or None,
        "left": p.get("total_qty"),
        "sizes": [s["name"] for s in p.get("size") or [] if s.get("has_quantity")] or None,
        "image": next(iter((p.get("images") or {}).get("large_default") or []), None),
        "url": f"{SITE}/BM-{p['id_product']}",
    }
    return {k: v for k, v in out.items() if v is not None}


async def _facets() -> dict[str, Any]:
    """The site's filter lists (category tree, brands, sizes), cached for an hour."""

    async def make() -> dict[str, Any]:
        body = await api("v4/products/", {"page_size": 1, "need_filter": 1})
        return body["data"]["filters"]

    return await cached("facets", FACET_TTL, make)


def _fold(text: str) -> str:
    """Lowercase and map Arabic ي/ك (used in many titles) to Persian ی/ک."""
    return text.replace("ي", "ی").replace("ك", "ک").lower()


async def _size_id(name: str) -> int:
    sizes = (await _facets())["sizes"]
    for s in sizes:
        if s["name"].strip().lower() == name.strip().lower():
            return s["id"]
    raise ApiError(f"Unknown size {name!r}. Examples: " + ", ".join(s["name"] for s in sizes[:12]) + ".")


async def _listing(
    *,
    query: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    sort: Sort = "relevance",
    in_stock: bool = True,
    min_price: int | None = None,
    max_price: int | None = None,
    size: str | None = None,
    page: int = 1,
    limit: int = 24,
) -> dict[str, Any]:
    params: dict[str, Any] = {"page": page, "page_size": limit}
    scan = bool(query) and sort in SORTS
    if query:
        params["q"] = query
    if category_id:
        params["filter[product_categories.id][eq]"] = category_id
    if brand_id:
        params["filter[product_manufacturer_id][eq]"] = brand_id
    if in_stock:
        params["filter[total_qty][gt]"] = 0
    if min_price is not None:
        params["filter[product_final_price][gte]"] = min_price * 10
    if max_price is not None:
        params["filter[product_final_price][lte]"] = max_price * 10
    if size:
        params["filter[available_sizes][in]"] = await _size_id(size)
    if sort in SORTS:
        direction, field = SORTS[sort]
        params[f"sort[{direction}]"] = field
    if scan:
        # The site matches the words loosely (category, tags); a price sort then floats unrelated items up.
        # Read sorted pages and keep rows that carry every word in title, brand or color.
        words = [_fold(w) for w in query.split()]
        rows, n = [], 1
        while True:
            data = (await api("v4/products/", {**params, "page": n, "page_size": 50}))["data"]
            for p in data["data"]:
                hay = _fold(f"{p.get('product_name')} {p.get('product_manufacturer_name')} {p.get('color_name')}")
                if all(w in hay for w in words):
                    rows.append(p)
            if len(rows) >= page * limit or n >= data["meta"]["last_page"] or n >= SCAN_PAGES:
                break
            n += 1
        return {
            "total": len(rows),
            "page": page,
            "pages": -(-len(rows) // limit),
            "products": [card(p) for p in rows[(page - 1) * limit : page * limit]],
        }
    data = (await api("v4/products/", params))["data"]
    meta = data["meta"]
    return {
        "total": meta["total"],
        "page": meta["current_page"],
        "pages": meta["last_page"],
        "products": [card(p) for p in data["data"]],
    }


_Q = Annotated[
    str,
    Field(
        min_length=2,
        max_length=100,
        description="Search words, Persian works best, e.g. 'مانتو مجلسی'.",
    ),
]
_SORT = Annotated[Sort, Field(description="'discount' = biggest saving first.")]
_STOCK = Annotated[bool, Field(description="Only products with stock.")]
_MIN = Annotated[int | None, Field(ge=0, description="Minimum price, Toman.")]
_MAX = Annotated[int | None, Field(ge=0, description="Maximum price, Toman.")]
_SIZE = Annotated[str | None, Field(max_length=20, description="Size label, e.g. 'M', '42', 'فری سایز'.")]
_PAGE = Annotated[int, Field(ge=1, le=200, description="Page number.")]
_LIMIT = Annotated[int, Field(ge=1, le=50, description="Products per page.")]


@tool("Search products")
async def bm_search(
    query: _Q,
    sort: _SORT = "relevance",
    in_stock: _STOCK = True,
    min_price: _MIN = None,
    max_price: _MAX = None,
    size: _SIZE = None,
    category_id: Annotated[int | None, Field(ge=1, description="Category id from bm_categories.")] = None,
    brand_id: Annotated[int | None, Field(ge=1, description="Brand id from bm_brands.")] = None,
    page: _PAGE = 1,
    limit: _LIMIT = 20,
) -> dict[str, Any]:
    """Search Banimode fashion products by keyword and return priced cards with discount, color and sizes in stock.

    Each card is one product in one color (ids repeat). Call bm_product for all colors and sizes.
    """
    return await _listing(
        query=query, category_id=category_id, brand_id=brand_id, sort=sort, in_stock=in_stock,
        min_price=min_price, max_price=max_price, size=size, page=page, limit=limit,
    )  # fmt: skip


@tool("Browse a category or brand")
async def bm_browse(
    category_id: Annotated[int | None, Field(ge=1, description="Category id from bm_categories.")] = None,
    brand_id: Annotated[int | None, Field(ge=1, description="Brand id from bm_brands.")] = None,
    sort: _SORT = "relevance",
    in_stock: _STOCK = True,
    min_price: _MIN = None,
    max_price: _MAX = None,
    size: _SIZE = None,
    page: _PAGE = 1,
    limit: _LIMIT = 20,
) -> dict[str, Any]:
    """List the products of a category and/or brand, with the same filters and cards as bm_search.

    Give category_id or brand_id (at least one).
    """
    if not category_id and not brand_id:
        raise ApiError("Give category_id (from bm_categories) or brand_id (from bm_brands).")
    return await _listing(
        category_id=category_id, brand_id=brand_id, sort=sort, in_stock=in_stock,
        min_price=min_price, max_price=max_price, size=size, page=page, limit=limit,
    )  # fmt: skip


def _flat_categories(tree: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Top-level nodes carry every descendant in a flat `items` list; return all nodes with their parent id."""
    out = []
    for top in tree:
        out.append({"id": top["id"], "name": top["name"], "level": top["level"], "parent_id": top.get("id_parent")})
        for c in top.get("items") or []:
            out.append({"id": c["id"], "name": c["name"], "level": c["level"], "parent_id": c.get("parent_id")})
    return out


async def _category_nodes() -> list[dict[str, Any]]:
    """Every category node. The unfiltered facets list only part of the tree (no مانتو, thin women's sections), but
    facets asked under a category list that branch in full, so read each child of the biggest section too."""

    async def make() -> list[dict[str, Any]]:
        tops = (await _facets())["categories"]
        nodes = _flat_categories(tops)
        big = max(tops, key=lambda t: len(t.get("items") or []))
        subs = [c["id"] for c in big.get("items") or [] if c["level"] == 3]

        async def branch(cid: int) -> list[dict[str, Any]]:
            body = await api(
                "v4/products/", {"page_size": 1, "need_filter": 1, "filter[product_categories.id][eq]": cid}
            )
            return _flat_categories(body["data"]["filters"]["categories"])

        for found in await asyncio.gather(*(branch(c) for c in subs)):
            nodes += found
        return list({n["id"]: n for n in nodes}.values())

    return await cached("category_nodes", FACET_TTL, make)


@tool("Product categories")
async def bm_categories(
    query: Annotated[str | None, Field(min_length=2, max_length=50, description="Name part, e.g. 'مانتو'.")] = None,
    parent_id: Annotated[int | None, Field(ge=1, description="List children of this category id.")] = None,
    limit: Annotated[int, Field(ge=1, le=100, description="Max categories.")] = 40,
) -> dict[str, Any]:
    """Find category ids by name, or walk the tree: no arguments lists the top sections, parent_id lists children.

    Pass an id to bm_browse or bm_search.
    """
    nodes = await _category_nodes()
    names = {n["id"]: n["name"] for n in nodes}
    if query:
        hits = [n for n in nodes if query.strip() in n["name"]]
    elif parent_id:
        hits = [n for n in nodes if n["parent_id"] == parent_id]
    else:
        hits = [n for n in nodes if n["level"] == min(x["level"] for x in nodes)]
    return {
        "total": len(hits),
        "categories": [{**n, "parent": names.get(n["parent_id"])} for n in hits[:limit]],
    }


@tool("Brands")
async def bm_brands(
    query: Annotated[
        str | None, Field(min_length=2, max_length=50, description="Brand name part, Persian or Latin.")
    ] = None,
    limit: Annotated[int, Field(ge=1, le=100, description="Max brands.")] = 40,
) -> dict[str, Any]:
    """Find brand ids by name (Persian or Latin), or list the first brands when no name is given.

    Pass the id as brand_id.
    """
    brands = (await _facets())["manufacturers"]
    if query:
        q = query.strip().lower()
        brands = [b for b in brands if q in b["name"].lower() or q in (b.get("en_name") or "").lower()]
    return {
        "total": len(brands),
        "brands": [{"id": b["id"], "name": b["name"], "en_name": b.get("en_name") or None} for b in brands[:limit]],
    }


@tool("Flash-sale deals")
async def bm_deals(
    page: Annotated[int, Field(ge=1, le=100, description="Page number (24 deals per page).")] = 1,
    limit: Annotated[int, Field(ge=1, le=24, description="Deals returned.")] = 24,
) -> dict[str, Any]:
    """List today's flash-sale products (deep time-limited discounts) with the time left.

    Use for "what is on sale right now"; call bm_product for sizes.
    """
    body = await api("v4/products/flash-sales-new", {"page": page})
    data = body["data"]
    meta = data["meta"]
    return {
        "total": meta["total"],
        "page": meta["current_page"],
        "pages": meta["last_page"],
        "ends_in_minutes": round((data.get("timer") or 0) / 60000) or None,
        "products": [card(p) for p in data["data"][:limit]],
    }
