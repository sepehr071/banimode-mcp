<!-- mcp-name: io.github.sepehr071/banimode-mcp -->

# banimode-mcp: Banimode MCP server for AI agents

**Unofficial, read-only MCP server that lets your AI agent shop for fashion on Banimode (بانی مد), a large Iranian online store.**
Search clothing, shoes, bags and accessories, compare real prices, check which sizes are in stock, read customer reviews and catch today's flash sales, all from Claude, Cursor or Copilot.

[![PyPI](https://img.shields.io/pypi/v/banimode-mcp?color=2563eb)](https://pypi.org/project/banimode-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/banimode-mcp)](https://pypi.org/project/banimode-mcp/)
[![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)](https://github.com/sepehr071/banimode-mcp/blob/main/LICENSE)

[Quick start](#quick-start) · [For AI agents](#for-ai-agents) · [Tools](#tools) · [FAQ](#faq) · [فارسی](#فارسی)

## For AI agents

- **What:** unofficial MCP server for Banimode (banimode.com, بانی مد), an Iranian fashion shop (clothing, shoes, bags, watches, beauty, home). Queries work best in Persian; prices are in Toman.
- **Install:** `claude mcp add banimode -- uvx banimode-mcp` (stdio transport, needs [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.10+).
- **Auth:** none. Optional `BANIMODE_MCP_PROXY` sets an HTTP proxy for requests to Banimode.
- **Access:** read-only. No login, cart, orders or posted reviews, so no write tools exist.
- **Tools:** 7, all prefixed `bm_`. Start with `bm_search`, `bm_browse` or `bm_deals`. Typical sequence: `bm_search` → `bm_product` → `bm_reviews`.
- **Use when:** comparing fashion prices, sizes in stock, discounts or reviews on Banimode.
- **Do not use when:** the user wants to buy (no cart or checkout) or needs a shipping fee (shown only at checkout).
- **Output:** compact JSON. `final_price` is what the buyer pays, `price` is before discount (left out when equal), `discount_pct` is a whole percent. A search card is one product in one color, so an id can repeat with other colors; `bm_product` lists every color with stock per size.
- **Machine-readable:** [`server.json`](server.json), and the catalog of all Iranian MCP servers at [awesome-iran-mcp](https://github.com/sepehr071/awesome-iran-mcp).

## Quick start

```bash
claude mcp add banimode -- uvx banimode-mcp
```

Or in any MCP client config:

```json
{ "mcpServers": { "banimode": { "command": "uvx", "args": ["banimode-mcp"] } } }
```

Banimode answers directly from Iran and from abroad. If your network needs a proxy, set `BANIMODE_MCP_PROXY=http://host:port` (a comma-separated list is tried in turn).

## Tools

| Tool | What it does |
|---|---|
| `bm_search` | Keyword search with sort (cheapest, expensive, discount, newest), Toman price range, size, in-stock, category and brand filters. |
| `bm_browse` | List a category and/or brand (ids from `bm_categories` / `bm_brands`) with the same filters. |
| `bm_categories` | Find category ids by name, or walk the tree by `parent_id`. |
| `bm_brands` | Find brand ids by Persian or Latin name. |
| `bm_deals` | Today's flash-sale products with discount and the time left. |
| `bm_product` | One product: every color with price, discount, stock per size, features, description. |
| `bm_reviews` | Customer reviews: stars, text, date, shop answer. |

## FAQ

**Are prices in Toman?** Yes. The site's API uses Rial; this server converts.

**Why does the same product appear twice?** Each card is one color of a product. `bm_product` shows all colors.

**Is it official?** No. It reads the open JSON API that the Banimode website itself uses. Keep request rates low.

## فارسی

سرور MCP غیررسمی و فقط‌خواندنی برای بانی‌مد (banimode.com): جستجوی لباس، کفش و اکسسوری، مقایسه قیمت به تومان، موجودی هر سایز، نظرات خریداران و تخفیف‌های فوری. نصب: `claude mcp add banimode -- uvx banimode-mcp`

## License

MIT
