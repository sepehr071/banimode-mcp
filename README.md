<!-- mcp-name: io.github.sepehr071/banimode-mcp -->

# banimode-mcp: Banimode MCP server for AI agents

**Let your AI agent shop for fashion on [Banimode](https://www.banimode.com) (بانی&zwnj;مد).**<br>
An unofficial, read-only MCP server for Banimode, an Iranian online fashion and lifestyle store: search clothing, shoes, bags and accessories,
compare prices in Toman, check which sizes are in stock, read customer reviews and catch today's flash sales, all from Claude, Cursor or Copilot.

[![PyPI](https://img.shields.io/pypi/v/banimode-mcp?color=2563eb)](https://pypi.org/project/banimode-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/banimode-mcp)](https://pypi.org/project/banimode-mcp/)
[![CI](https://github.com/sepehr071/banimode-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sepehr071/banimode-mcp/actions/workflows/ci.yml)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.sepehr071%2Fbanimode--mcp-7c3aed)](https://registry.modelcontextprotocol.io/?q=banimode-mcp)
[![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)](https://github.com/sepehr071/banimode-mcp/blob/main/LICENSE)

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=banimode&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJiYW5pbW9kZS1tY3AiXX0=)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_banimode--mcp-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=banimode&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22banimode-mcp%22%5D%7D)

[For AI agents](#for-ai-agents) · [Why](#why) · [What it can do](#what-it-can-do) · [Quick start](#quick-start) · [Tools](#tools) · [FAQ](#faq) · [فارسی](#فارسی)

---

## For AI agents

- **What:** unofficial MCP server for Banimode (banimode.com, بانی&zwnj;مد), an Iranian fashion shop (clothing, shoes, bags, watches, beauty, home). Queries work best in Persian; prices are in Toman.
- **Install:** `uvx banimode-mcp` or `claude mcp add banimode -- uvx banimode-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none, no API key or account. Optional `BANIMODE_MCP_PROXY` (HTTP proxy, or a comma-separated list tried in turn).
- **Access:** read-only. No login, cart, orders or posted reviews, so no confirmation is needed before calling any tool.
- **Tools:** 7, all prefixed `bm_`. Start with `bm_search`, `bm_browse` or `bm_deals`. Typical sequence: `bm_search` -> `bm_product` -> `bm_reviews`.
- **Use when:** comparing fashion prices, sizes in stock, discounts or reviews on Banimode.
- **Do not use when:** the user wants to buy (no cart or checkout) or needs the shipping fee (shown only at checkout).
- **Output:** compact JSON. Prices in Toman: `final_price` is what the buyer pays, `price` is the list price before discount (left out when equal), `discount_pct` is a whole percent. A search card is one product in one color, so an id can repeat with other colors; `bm_product` lists every color with stock per size.
- **Machine-readable:** [`server.json`](https://github.com/sepehr071/banimode-mcp/blob/main/server.json) and the
  [awesome-iran-mcp catalog](https://github.com/sepehr071/awesome-iran-mcp) (`TOOLS.md`, `servers.json`, `llms.txt`).

## Why

Fashion shopping means many tabs: the same dress in five colors, sizes that are sold out, a discount that may or may not be real,
and reviews buried at the bottom of the page. With `banimode-mcp` an agent filters by price and size, hides sold-out items,
sorts by discount and reads the reviews for you, then gives you a short list with links.

## What it can do

- **Search** by keyword with sort (cheapest, most expensive, biggest discount, newest), a Toman price range, size, in-stock, category and brand filters
- **Browse** a category and/or a brand, using ids from `bm_categories` and `bm_brands`
- **Check a product**: every color with price, discount, stock per size, features and a short description
- **Read reviews**: stars, text, date and the shop's answer
- **Catch flash sales**: today's time-limited discounts with the time left
- **Read-only by design**: no login, no cart, no orders

Example prompts:

- "Find women's black sneakers on Banimode under 2 million Toman, size 38 in stock, biggest discount first."
- "What are today's flash sales on Banimode? Show only the ones with more than 40% off."
- "Show me the reviews of this product and tell me if the sizing runs small."
- <span dir="rtl">مانتو مجلسی زنانه زیر ۳ میلیون تومان در بانی&zwnj;مد پیدا کن.</span>
- <span dir="rtl">ارزان&zwnj;ترین کفش اسپرت مردانه سایز ۴۳ که موجود باشد کدام است؟</span>
- <span dir="rtl">تخفیف&zwnj;های فوری امروز بانی&zwnj;مد را نشان بده.</span>

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). No API key or account.

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add banimode -- uvx banimode-mcp
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Settings -> Developer -> Edit Config, then add:

```json
{
  "mcpServers": {
    "banimode": { "command": "uvx", "args": ["banimode-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Cursor</b></summary>

Click **Install in Cursor** above, or add the Claude Desktop block to `~/.cursor/mcp.json`.
</details>

<details>
<summary><b>VS Code (Copilot agent mode)</b></summary>

Click **Install in VS Code** above, or add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "banimode": { "type": "stdio", "command": "uvx", "args": ["banimode-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
codex mcp add banimode -- uvx banimode-mcp
```

Or in `~/.codex/config.toml`:

```toml
[mcp_servers.banimode]
command = "uvx"
args = ["banimode-mcp"]
```
</details>

<details>
<summary><b>Gemini CLI</b></summary>

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "banimode": { "command": "uvx", "args": ["banimode-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Windsurf</b></summary>

Add the Claude Desktop block to `~/.codeium/windsurf/mcp_config.json`.
</details>

<details>
<summary><b>Anything else</b></summary>

It is a standard stdio MCP server: run `uvx banimode-mcp`, or `pip install banimode-mcp` and run `banimode-mcp`.
</details>

## Tools

| Tool | What it does |
|---|---|
| `bm_search` | Search Banimode fashion products by keyword and return priced cards with discount, color and sizes in stock. Sort, price range, size, in-stock, category and brand filters. |
| `bm_browse` | List the products of a category and/or brand (ids from `bm_categories` / `bm_brands`), with the same filters and cards as `bm_search`. |
| `bm_categories` | Find category ids by name, or walk the tree: no arguments lists the top sections, `parent_id` lists children. |
| `bm_brands` | Find brand ids by name (Persian or Latin), or list the first brands when no name is given. |
| `bm_deals` | List today's flash-sale products (deep time-limited discounts) with the time left. |
| `bm_product` | Get one product: every color with its price, discount, stock per size, features and short description. |
| `bm_reviews` | Read customer reviews of a product: stars (1-5, null if only text), text, date and the shop's answer. |

## How it works

```text
  AI agent  (Claude, Cursor, Copilot, ...)
      │
      │  MCP over stdio
      ▼
  banimode-mcp  (runs on your machine)
      │
      │  HTTPS
      └──────▶  mobapi.banimode.com   products, categories, brands, deals, reviews
```

`banimode-mcp` runs locally and calls the open JSON API that the banimode.com website itself uses. There is no hosted server in between
and no API key. Requests are throttled and retried on timeouts, 429 and 5xx.

## Good to know

- **Prices are in Toman.** The API uses Rial; the server divides by 10 so numbers match the website.
- **One card per color.** The same product id can appear several times in a list; call `bm_product` for all colors and sizes.
- **Sold-out items are hidden by default** (`in_stock` is true), because sorting by price otherwise starts with unavailable items.
- **Persian queries match best** (`مانتو مجلسی`, `کفش اسپرت مردانه`).
- **Results are capped at 10,000 per query**, and a page holds at most 50 products (default 20, to keep answers small).
- **Flash-sale prices are time limited**; the tool returns the minutes left.
- **Shipping fee is not included.** It is only shown at checkout, so the real cost is `final_price` plus an unknown shipping fee.
- **Review and description text comes from the site and its users**; the server tells the agent to treat it as data, not instructions.
- **Not supported:** login, cart, orders, wishlist, wallet, posting reviews.
- **Proxy:** system proxy variables are ignored on purpose; set `BANIMODE_MCP_PROXY` if you need one.

## FAQ

<details>
<summary><b>Is there a Banimode API or MCP server for AI agents?</b></summary>

Yes: `banimode-mcp` is an unofficial MCP server with 7 read-only tools for search, categories, brands, flash sales, product details and reviews.
It calls the same JSON API the banimode.com site uses; no API key is needed.
</details>

<details>
<summary><b>How do I use Banimode with Claude, Cursor or Copilot?</b></summary>

Add the server with `claude mcp add banimode -- uvx banimode-mcp` (or the matching config in [Quick start](#quick-start)), then ask in plain language, in Persian or English.
</details>

<details>
<summary><b>Is it official, safe and free?</b></summary>

It is unofficial and not affiliated with Banimode. It is read-only (no login, cart or orders), runs on your machine and is free under the MIT license.
</details>

<details>
<summary><b>Are prices in Toman?</b></summary>

Yes. The site's API uses Rial; this server converts to Toman.
</details>

<details>
<summary><b>Why does the same product appear twice?</b></summary>

Each search card is one color of a product. `bm_product` shows all colors with stock per size.
</details>

<details>
<summary><b>Can it buy something for me?</b></summary>

No, and that is deliberate. There is no login and no cart or checkout call. The agent finds the best option; you order on the site.
</details>

<details>
<summary><b>Do I need an Iranian IP?</b></summary>

No: the API answered directly from Iran and through a foreign (Turkish) proxy in testing, and there was no bot challenge. If your network needs a proxy, set `BANIMODE_MCP_PROXY`.
</details>

<details>
<summary><b>Does it show the shipping fee?</b></summary>

No. Banimode shows shipping only at checkout, so the tools return product prices without shipping.
</details>

<details>
<summary><b>Claude Desktop says <code>uvx</code> is not found</b></summary>

Use the full path to `uvx` (`where uvx` on Windows, `which uvx` on macOS/Linux) as `command`.
</details>

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `BANIMODE_MCP_PROXY` | unset | Optional HTTP proxy URL, or a comma-separated list tried in turn, for banimode.com. System proxies are ignored. |

<a id="فارسی"></a>

## فارسی: سرور MCP بانی&zwnj;مد

<div dir="rtl">

**banimode-mcp** یک سرور MCP غیررسمی و فقط&zwnj;خواندنی برای بانی&zwnj;مد (banimode.com)، فروشگاه اینترنتی مد و پوشاک در ایران، است.
این سرور به دستیار هوش مصنوعی شما (Claude، Cursor، Copilot و ...) اجازه می&zwnj;دهد در بانی&zwnj;مد لباس، کفش، کیف و اکسسوری جستجو کند،
قیمت&zwnj;ها را به تومان مقایسه کند، موجودی هر سایز را ببیند، نظرات خریداران را بخواند و تخفیف&zwnj;های فوری را پیدا کند.

**چه کارهایی می&zwnj;کند**

- جستجوی کالا با مرتب&zwnj;سازی (ارزان&zwnj;ترین، گران&zwnj;ترین، بیشترین تخفیف، جدیدترین) و فیلتر محدوده قیمت، سایز، موجودی، دسته و برند.
- مرور یک دسته یا برند، و پیدا کردن شناسه دسته&zwnj;ها و برندها.
- جزئیات کالا: همه رنگ&zwnj;ها با قیمت، تخفیف، موجودی هر سایز، ویژگی&zwnj;ها و توضیح کوتاه.
- نظرات خریداران با ستاره، متن، تاریخ و پاسخ فروشگاه.
- تخفیف&zwnj;های فوری امروز با زمان باقی&zwnj;مانده.

**نکته&zwnj;ها**

- فقط خواندنی است: وارد حساب نمی&zwnj;شود، سبد خرید نمی&zwnj;سازد و سفارش ثبت نمی&zwnj;کند.
- همه قیمت&zwnj;ها به تومان است. هزینه ارسال فقط هنگام پرداخت در سایت مشخص می&zwnj;شود و در نتیجه&zwnj;ها نیست.
- جستجوی فارسی بهترین نتیجه را می&zwnj;دهد.
- روی سیستم خود شما اجرا می&zwnj;شود و کلید API لازم ندارد.

**نصب** (اول [uv](https://docs.astral.sh/uv/getting-started/installation/) را نصب کنید). در Claude Code:

</div>

```bash
claude mcp add banimode -- uvx banimode-mcp
```

<div dir="rtl">

در Claude Desktop، Cursor و بقیه برنامه&zwnj;ها همان تنظیم بخش [Quick start](#quick-start) را بگذارید.

**نمونه پرسش&zwnj;ها**

- «مانتو مجلسی زنانه زیر ۳ میلیون تومان در بانی&zwnj;مد پیدا کن.»
- «ارزان&zwnj;ترین کفش اسپرت مردانه سایز ۴۳ که موجود باشد کدام است؟»
- «تخفیف&zwnj;های فوری امروز بانی&zwnj;مد را نشان بده.»

**کلیدواژه&zwnj;ها:** بانی مد، بانی&zwnj;مد، خرید لباس آنلاین، فروشگاه اینترنتی مد و پوشاک، مانتو، کفش، کیف، قیمت لباس، تخفیف فوری، سرور MCP، هوش مصنوعی.

</div>

## Development

```bash
git clone https://github.com/sepehr071/banimode-mcp && cd banimode-mcp
uv sync
uv run python -m pytest            # offline, against recorded responses
uv run python -m pytest -m live    # real API
uv run ruff check .
```

Tools live in `src/banimode_mcp/catalog.py` and `product.py`; each is a typed async function with a docstring that tells the agent when to use it.
Issues and PRs are welcome.

Releases: bump the version in `pyproject.toml` and `server.json`, then push a `v*` tag. GitHub Actions publishes to PyPI and the
[MCP Registry](https://registry.modelcontextprotocol.io) and creates the GitHub Release.

## Related servers

- [awesome-iran-mcp](https://github.com/sepehr071/awesome-iran-mcp): catalog of all Iranian-service MCP servers
- [Digikala MCP server](https://github.com/sepehr071/digikala-mcp) for Iran's largest online store
- [Khanoumi MCP server](https://github.com/sepehr071/khanoumi-mcp) for beauty and personal care
- [Torob MCP server](https://github.com/sepehr071/torob-mcp) for price comparison across shops
- [Shopino MCP server](https://github.com/sepehr071/shopino-mcp) for fashion shopping
- [Basalam MCP server](https://github.com/sepehr071/basalam-mcp) for a marketplace of independent sellers

## Disclaimer

Unofficial and not affiliated with or endorsed by Banimode. It uses the open JSON API of the banimode.com website, which can change without notice.
Please keep request rates reasonable.

## License

[MIT](https://github.com/sepehr071/banimode-mcp/blob/main/LICENSE)
