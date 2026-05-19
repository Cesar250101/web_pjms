# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Module identity

`web_pjms` is an Odoo 16 module that renders the full PJMS storefront (Chilean homewear/sleepwear brand). It is **website-scoped**: every override checks `website.name == 'PJMS'` so installing it on a multi-website instance must not affect the other sites.

- Manifest version is the contract: bumping `version` in `__manifest__.py` triggers the matching script under `migrations/<version>/post-migrate.py` on `-u web_pjms`.
- Depends on `website`, `website_sale`, and `web_taller4` — the latter is a sibling internal module, not on PyPI/OCA.

## Common commands

Run from a shell that has the Odoo venv active (Windows host, `python` resolves to Odoo's interpreter):

```powershell
# Install / upgrade only this module against a database
python "c:\Program Files\Odoo 16\server\odoo-bin" -c odoo.conf -d <db> -u web_pjms --stop-after-init

# Drop module assets cache after SCSS changes (no server restart needed in dev)
# Visit /web#action=base.open_module_tree, then "Update Apps List" + Upgrade web_pjms

# Run a single Python module test (no .tests folder ships today — add tests under tests/ first)
python "c:\Program Files\Odoo 16\server\odoo-bin" -c odoo.conf -d <db> --test-tags web_pjms --stop-after-init
```

There is no lint/test/build pipeline checked in — Odoo's own `--test-tags` is the only test runner.

## Architecture — the big picture

### 1. Site isolation pattern
Every visual override lives inside `views/layout/pj_layout.xml` and similar inheritance templates, gated by `t-if="website and website.name == 'PJMS'"`. When adding a new layout tweak, **never edit `website.layout` unconditionally** — always wrap in that guard, otherwise the override leaks to every website on the instance. The body class `pj-body` and header class `pj-odoo-header` are the scoping anchors for SCSS — all `web_pjms` SCSS must descend from one of those classes.

### 2. Data lifecycle: data files vs. hooks vs. migrations
Three mechanisms touch the database, with overlapping responsibilities — pick deliberately:

- **`data/website_data.xml`** — declares the `website` record (`PJMS`). `noupdate="1"` so re-upgrades won't overwrite manual changes in the backend.
- **`hooks.py::post_init_hook`** — runs **once on install**. Creates `product.public.category` records (with base64 images from `static/src/img/categories/`), the top menu items (`/shop`, `/contactus`), and per-category menus under `/coleccion/<id>`. It is idempotent: every create is preceded by a `search` check.
- **`migrations/<version>/post-migrate.py`** — runs on every `-u` after the manifest version is bumped. They **re-invoke** `_ensure_categories` and `_ensure_category_menus` from `hooks.py`, then patch view keys via raw SQL (`UPDATE ir_ui_view SET key=...`) because Odoo silently mangles `key` when a view's `website_id` is set. If you add a new page template that breaks on upgrade, the fix usually goes here.

When adding a new module version: bump `__manifest__.py::version`, create `migrations/<new-version>/post-migrate.py` (copy the previous one as scaffold), and add only the **delta** the upgrade requires. The shared `_ensure_*` helpers in `hooks.py` are the single source of truth for category/menu seeding.

### 3. Controllers — two layers
[controllers/main.py](controllers/main.py) has two classes that serve different roles:

- `WebsiteSalePjms(WebsiteSale)` — extends the native `/shop` to support `?ribbon_tipo=<value>` filtering. **Critical**: in Odoo 16, `/shop` does NOT use `_get_search_domain` to fetch the product list — it goes through `_shop_lookup_products` → `website._search_with_fuzzy("products_only", ...)`, which only honors `category`, `min_price`, `max_price`, and `attrib_values`. The actual ribbon filter is applied by overriding `_shop_lookup_products` and post-filtering the returned recordset. `_get_search_domain` is still overridden because it feeds the **price slider range** (so the slider reflects only the filtered subset). The four overrides (`_shop_lookup_products`, `_get_search_domain`, `_shop_get_query_url_kwargs`, `_get_additional_extra_shop_values`) form a set that **must stay in sync** — list filter, slider range, URL preservation across pagination, and template value. Forgetting any one breaks a specific behavior.
- `PjmsSite` — public routes for `/pjms`, `/contacto-pjms`, `/coleccion/<category>`. The category route includes a cross-site guard (`category.website_id.id != website.id` → redirect `/shop`) and forces CLP currency.

### 4. Ribbon system
`product.ribbon` is extended (`models/product_ribbon.py`) with a `tipo` selection: `mas_vendidos`, `especial`, `en_descuento`, `otros` — plus `nuevo` inherited from `website_sale.new_ribbon` (set via `data/ribbon_data.xml`). The `tipo` field is the **filter key** that `/shop?ribbon_tipo=...` and `s_pj_bestsellers` use to surface curated product strips. To add a new ribbon category: extend the selection, add a `selection_add` entry **with ondelete**, and the controller filter works automatically.

### 5. Snippet authoring conventions
Each snippet is a triple of files with matching names:
```
views/snippets/s_pj_<name>.xml          — <template id="s_pj_<name>"> with t-snippet markup
static/src/scss/snippets/s_pj_<name>.scss — styles, scoped under .pj-body
views/snippets/snippets.xml             — register in the PJMS panel
```
Snippets are registered into the editor via inheritance of `website.snippets` (see `snippets.xml`) — adding a new snippet requires a new `<t t-snippet="...">` entry there or it won't appear in the editor.

### 6. Asset bundle order matters
In `__manifest__.py::assets`:
- `primary_variables.scss` is **prepended** (loads before Odoo's own variables — needed for `$o-theme-color-palettes` overrides to win).
- `pj_tokens.scss` comes next (PJMS-specific CSS vars).
- Then `pj_layout.scss`, then `pj_section_common.scss`, then per-snippet SCSS.
- `website_sale.scss` last — it overrides shop visuals once everything else is loaded.

When adding SCSS: respect this order. A new theme token belongs in `pj_tokens.scss`; a section-wide helper in `pj_section_common.scss`; snippet-local styles stay in the snippet's own file.

## Brand reference (used in SCSS tokens)
Colors: slate `#7890a8`, forest `#003030`, teal `#78c0c0`, blush `#f0d8d8`, mustard `#f0a800`, cream `#faf7f5`.
Fonts (Google Fonts, injected only on PJMS site via `pj_google_fonts` template): Italiana (display), Sacramento (script), Playfair Display, Material Symbols Outlined.

## Gotchas

- **View `key` corruption**: When a page template has `<template id="pj_home">` and is created as `website_id`-bound at runtime, Odoo can rewrite `key` to something other than `web_pjms.pj_home`. The migration scripts force-correct this via raw SQL — if `request.render('web_pjms.pj_home')` ever 404s after an upgrade, that is the cause.
- **Category menu URLs**: parent categories use `/coleccion/<id>` (handled by `PjmsSite.category_page`), children use `/shop?category=<id>` (native website_sale). Mixing the two breaks the header's "active" detection.
- **Uninstall is destructive**: `uninstall_hook` unlinks **all** `product.public.category` records bound to the PJMS website. Do not test uninstall on a database where categories have been hand-curated unless they are backed up.
- **`request.website` is not available in the snippet editor preview**: The website editor renders snippet thumbnails via `ir.ui.view.render_public_asset()`, which does **not** set `request.website`. Any snippet template that does `request.website.id` crashes the editor with `AttributeError: 'Request' object has no attribute 'website'` the moment you open the page in edit mode — even though the same snippet renders fine on the public-facing page. Use `request.env['website'].get_current_website().id` instead (capture it once in a `t-set="pj_website_id"` at the top of the template, then reuse). All current PJMS snippets that query `product.template` follow this pattern — replicate it in any new snippet that needs the current website id.
