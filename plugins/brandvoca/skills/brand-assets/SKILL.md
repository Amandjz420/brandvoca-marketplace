---
name: brandvoca-brand-assets
description: >
  Use this skill when the user wants to generate or refine a specific brand asset.
  Trigger phrases: "generate a logo", "make me a logo", "generate color palette",
  "refine the palette", "new typography", "generate brand names", "suggest names for my brand",
  "generate website UI", "create landing page design", "regenerate the logo",
  "I want a different color palette", "refine my logo", "try a different logo style",
  "generate all logos", "show me logo options", "generate brand kit", "create design system",
  "generate UI kit", "show me the brand kit", "refine the brand kit", "check domain availability",
  "is this domain taken", "export logo as SVG", "get SVG", "set logo as primary reference".
  Also use for any publishing action: "publish this palette", "publish the logo",
  "make this the active brand name", "publish the brand kit".
metadata:
  version: "1.0.0"
---

# BrandVoca Brand Assets

Generate, refine, and publish specific brand assets for an existing brand.

## Available Tools

| Tool | What it does |
|------|-------------|
| `generate_color_palette` | Generate/refine a color system using Gemini |
| `get_color_palette` | Get a specific palette version by ID |
| `list_color_palettes` | List all palette versions (draft + published) |
| `publish_color_palette` | Publish a palette version |
| `generate_typography` | Generate/refine a font-pairing system using Gemini |
| `get_typography` | Get a specific typography version by ID |
| `list_typographies` | List all typography versions |
| `publish_typography` | Publish a typography version |
| `generate_brand_names` | Generate AI name suggestions using Grok (5 categories) |
| `get_brand_name` | Get a specific brand name version by ID |
| `list_brand_names` | List all name versions |
| `publish_brand_name` | Publish a name (propagates across all brand assets) |
| `check_domain` | Check domain availability + pricing for a brand name (10 credits) |
| `domain_suggestions` | Get available alternative domains with prefix/suffix combos (10 credits) |
| `generate_logo` | Generate a logo image in one of 6 styles using Gemini |
| `get_logo` | Get a specific logo version by ID (includes image_url + concept) |
| `list_logos` | List all logo versions (filter by style/status) |
| `publish_logo` | Publish a logo version |
| `upload_primary_logo` | Upload/replace the primary logo reference image |
| `delete_primary_logo` | Remove the primary logo reference image |
| `set_logo_as_primary` | Promote a generated logo to the primary reference image |
| `get_logo_svg` | Generate SVG of logo symbol — 15 credits first time, free after (cached) |
| `generate_website_ui` | Generate a landing page hero section UI image |
| `get_website_ui` | Get a specific website UI version by ID |
| `list_website_uis` | List all website UI versions |
| `generate_brand_kit` | Generate a complete design system / UI kit using Gemini |
| `get_brand_kit` | Get a specific brand kit version by ID |
| `list_brand_kits` | List all brand kit versions (draft + published) |
| `publish_brand_kit` | Publish a brand kit version |
| `rate_asset` | Rate any asset as positive/negative (thumbs up/down) |

## Prerequisites

Before generating assets, the brand needs:
- A completed and submitted questionnaire
- A generated brand analysis (Step 3)

For logo and website UI generation, also needed:
- Published color palette (Step 4)
- Published typography (Step 5)

For brand kit generation, also needed:
- Published color palette (Step 4)
- Published typography (Step 5)
- Brand analysis (Step 3)

If prerequisites are missing, tell the user which step to complete first.

## Primary Logo (Reference Image)

Before generating logos, the user can optionally upload a reference logo image. This gives Gemini a visual starting point.

### Uploading a Reference Logo
- Call `upload_primary_logo(brand_id, file_path="...")`.
- Accepted formats: .png, .jpeg, .webp, .svg (max 10 MB).
- This replaces any previously uploaded reference logo.
- The reference is used by Gemini during logo generation for style/color cues.

### Removing a Reference Logo
- Call `delete_primary_logo(brand_id)`.
- After removal, Gemini will generate logos purely from the brand analysis.

### Promoting a Generated Logo to Primary
- After the user likes a generated logo, offer to set it as the primary reference:
  "Want me to set this logo as your primary reference? Future generations will build on it."
- Call `set_logo_as_primary(brand_id, logo_id)`.
- This copies the AI-generated image directly from storage — no URL round-trip needed.

## Logo Generation

### Generating a Logo

Always ask which style the user wants if they haven't specified:

| Style | Description | Best for |
|-------|-------------|----------|
| `flat_vector` | Clean flat vector, 3 versions (horizontal, symbol, stacked) | Most versatile, recommended first |
| `geometric_minimal` | Purely geometric shapes, mathematical balance | Tech, finance, SaaS |
| `abstract_symbolic` | Interlocking geometry from brand values | Agencies, consultancies |
| `bold_wordmark` | Typography-first, custom letterform adjustments | Consumer brands, apps |
| `minimal_mascot` | Shape-based minimal character | Community, lifestyle brands |
| `dynamic_motion` | Directional geometry suggesting movement | Sports, logistics, innovation |

Call `generate_logo(brand_id, style)`. This takes 20–60 seconds — set expectations.

### Refinement Loop

When the user wants to tweak a logo:
1. Get the current logo's ID from `list_logos(brand_id, style="...")` or from the previous generation response.
   - To view a specific version's details: `get_logo(brand_id, logo_id)`.
2. Ask for specific feedback (colors too dark? symbol unclear? typography too thin?).
3. Call `generate_logo(brand_id, style, user_feedback="...", previous_version_id="...")`.
4. Compare the new version to the previous one.
5. Publish with `publish_logo(brand_id, logo_id)` when happy.

### Generating All 6 Styles

If user wants to see all options:
- Warn this will make 6 separate Gemini calls and take several minutes.
- Generate them sequentially: flat_vector → geometric_minimal → abstract_symbolic → bold_wordmark → minimal_mascot → dynamic_motion.
- Present all 6 image URLs in a gallery-style list with their style names.

### SVG Export (Pro/Max Plan Only)

After showing a logo the user likes, offer SVG export:
- "Want an SVG version of the logo symbol? First generation costs 15 credits, then it's free (cached)."
- Call `get_logo_svg(brand_id, logo_id)`.
- The response includes:
  - `svg_url` — the SVG file URL (link it directly)
  - `symbol_url` — symbol-only PNG (by-product of extraction)
  - `cached: true` — no credits deducted (already generated)
- Free plan users will see a 403 error with `upgrade_required: true` — tell them SVG export requires Pro or Max.

## Domain Availability (After Brand Name)

After publishing a brand name, proactively offer domain availability checking:

### Checking Primary Domains
- Call `check_domain(brand_id, name="brandname")` — name should be lowercase, no spaces, no TLD.
- Costs 10 credits. Checks: com, net, org, io, co, app, dev, ai, xyz.
- Present results in a clean format:

```
**Domain Availability for "brandvoca"**

✅ brandvoca.com   — ₹750/yr register · ₹1,100/yr renew
❌ brandvoca.net   — Taken
✅ brandvoca.io    — ₹3,500/yr register · ₹4,200/yr renew
❌ brandvoca.co    — Taken
✅ brandvoca.app   — ₹1,200/yr register
```

### Getting Domain Suggestions (When Primary TLDs Are Taken)
- Call `domain_suggestions(brand_id, name="brandname", max_suggestions=10)`.
- Returns available alternatives with prefixes (get-, my-, the-, try-, use-, go-, hey-) and suffixes (-app, -hq, -hub, -pro, -ai).
- Only shows available domains with pricing. Costs 10 credits.

Example output:
```
**Available Alternatives**
✅ getbrandvoca.com  — ₹750/yr
✅ brandvocahq.io   — ₹3,500/yr
✅ mybrandvoca.app  — ₹1,200/yr
```

## Color Palette

### Generating / Refining

Call `generate_color_palette(brand_id)` for a fresh palette.

For refinement:
1. Get the current palette ID from `list_color_palettes(brand_id)`.
   - To view a specific version's details: `get_color_palette(brand_id, palette_id)`.
2. Collect specific feedback: too dark, wrong mood, clashes with brand values, etc.
3. Call `generate_color_palette(brand_id, user_feedback="...", previous_version_id="...")`.
4. Show the new `core_palette` colors with hex codes.
5. Publish with `publish_color_palette(brand_id, palette_id)`.

### Presenting Color Palette Results

Extract and show:
- Core palette: name + hex for each color
- Color rationale summary (1-2 sentences)

Example format:
```
**Core Palette**
- Deep Navy `#1A2B4C` — primary backgrounds and headings
- Electric Blue `#2563EB` — CTAs and interactive elements
- Warm White `#F8F7F4` — surface and body backgrounds
- Slate `#64748B` — secondary text

*"The palette balances trust and innovation through navy stability
with electric blue energy, grounded in warm neutrals."*
```

## Typography

### Generating / Refining

Same flow as color palette: generate → review → refine if needed → publish.

To view a specific typography version: `get_typography(brand_id, typography_id)`.

For refinement feedback examples: "Google Fonts only", "more geometric headings", "better contrast between heading and body", "more professional".

### Presenting Typography Results

Extract and show:
- Primary typeface (headings): name + style description
- Secondary typeface (body): name + style description
- Accent typeface (if enabled)
- Font pairing rationale (1 sentence)

## Brand Names

### Generating Suggestions

Call `generate_brand_names(brand_id)`.

To view a specific name version: `get_brand_name(brand_id, name_id)`.

Present the 5 categories clearly. For each name show the name + rationale:

```
**Descriptive** — clear, literal names
• BrandForge — forging brand identities, implies craft and strength
• IdentityLab — laboratory approach to brand creation

**Invented / Abstract**
• Voqua — distinctive, invented word with no prior associations
...
```

### Publishing a Name

Once the user picks a name:
1. Ask them to confirm: "Are you sure you want to publish '[Name]'? This will update all existing brand assets."
2. Call `publish_brand_name(brand_id, name_id, name="Chosen Name")`.
3. Confirm the change: "Done — all palettes, typography, and logos have been updated to use '[Name]'."
4. Offer domain check: "Want me to check domain availability for '[chosen-name]'? (10 credits)"

## Website UI

### Generating

Call `generate_website_ui(brand_id)`. Takes 20–60 seconds.

The result is a 1440px desktop hero section mockup containing:
- Navigation bar (logo area + 3–5 links + CTA button)
- Hero content (headline + subline + CTA)
- Visual system element (geometric composition or brand-derived graphic)

Present the `image_url` as a clickable link and show the `concept` text below it.

To view a specific website UI version: `get_website_ui(brand_id, ui_id)`.

### Refinement

For refinement, common feedback directions:
- Layout: "more asymmetric", "center the headline", "bigger hero text"
- Color: "darker background", "use more of the accent color"
- Style: "more minimal", "less geometric in the background", "add more whitespace"
- Mood: "feel more premium", "less corporate, more human"

## Brand Kit (Design System)

### What It Generates

The brand kit is a complete design system / UI kit with 14 sections:
- **meta** — brand name, tagline, version metadata
- **colors** — core palette swatches + semantic color tokens (CSS variables using HSL)
- **typography** — type scale, font pairings, specimen examples
- **spacing** — spacing scale, layout grid, container widths
- **buttons** — primary/secondary/ghost/destructive button variants with TSX code
- **forms** — input fields, selects, checkboxes, radio buttons with TSX code
- **modals** — dialog, confirmation, drawer patterns with TSX code
- **cards** — content card, pricing card, feature card variants with TSX code
- **navigation** — navbar, sidebar, breadcrumbs, pagination with TSX code
- **alertsAndBadges** — alert banners, toast notifications, status badges with TSX code
- **interactions** — hover states, transitions, loading patterns
- **pageTemplates** — hero section, features grid, pricing page layouts with TSX code
- **designPrinciples** — guiding principles for the design system
- **howToUse** — developer quick-start guide for using the kit

All TSX code uses Tailwind CSS with custom brand tokens via CSS variables (e.g., `hsl(var(--coral))`).

### Generating

Call `generate_brand_kit(brand_id)`. This is the most comprehensive generation — takes 30–90 seconds.

Prerequisites (all required):
1. Brand analysis must exist (Step 3)
2. Published color palette (Step 4)
3. Published typography (Step 5)

If any prerequisite is missing, the API returns an error explaining what's needed.

### Presenting Results

The response contains all 14 sections. Don't dump the entire JSON — instead:
- Summarize the meta info (brand name, tagline)
- List the core palette colors with their CSS variable names
- Mention the number of component categories generated
- Offer to show specific sections in detail: "Want to see the button components, card layouts, or page templates?"

### Refinement

When the user wants to refine the brand kit:
1. Get the current kit ID from `list_brand_kits(brand_id)` or the previous generation response.
   - To view a specific version: `get_brand_kit(brand_id, kit_id)`.
2. Ask for specific feedback: "buttons too rounded?", "need darker backgrounds?", "cards need more padding?", "navigation should be more minimal?"
3. Call `generate_brand_kit(brand_id, user_feedback="...", previous_version_id="...")`.
4. Show what changed in the new version.
5. Publish with `publish_brand_kit(brand_id, kit_id)` when happy.

### Publishing

Call `publish_brand_kit(brand_id, kit_id)`. Only one brand kit can be published per brand at a time — publishing a new version automatically un-publishes the previous one.

## Rating Assets (Thumbs Up / Down)

After showing any generated asset, ask the user if they like it. If they express a clear positive or negative reaction, call `rate_asset` to record the feedback.

| asset_type | asset_id required? | When to use |
|---|---|---|
| `analysis` | No | After presenting the brand analysis |
| `color_palette` | Yes (palette UUID) | After showing a palette |
| `typography` | Yes (typography UUID) | After showing font pairings |
| `brand_name` | Yes (brand name UUID) | After showing name suggestions |
| `logo` | Yes (logo UUID) | After showing a logo image |
| `website_ui` | Yes (website UI UUID) | After showing the hero mockup |
| `brand_kit` | Yes (brand kit UUID) | After showing the design system |

**Usage pattern:**
```
user: "I love this logo!"
→ rate_asset(brand_id, "logo", "positive", logo_id)
→ "Great, I've marked this as a favorite."

user: "The colors feel wrong."
→ rate_asset(brand_id, "color_palette", "negative", palette_id)
→ Offer to generate a refined version with feedback.
```

Don't ask explicitly "would you like to rate this?" — just record feedback naturally when the user expresses clear approval or disapproval.

## Publishing Rules

| Asset | One published at a time? | How to change |
|-------|--------------------------|---------------|
| Color Palette | Yes (per brand) | Publish new version — old auto-unpublishes |
| Typography | Yes (per brand) | Publish new version — old auto-unpublishes |
| Brand Name | Yes (per brand) | Publish new version — old auto-unpublishes |
| Logo | Yes per style (6 slots) | Publish new version of same style |
| Website UI | No publish concept | All versions are equal |
| Brand Kit | Yes (per brand) | Publish new version — old auto-unpublishes |
