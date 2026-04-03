---
name: brandvoca-brand-assets
description: >
  Use this skill when the user wants to generate or refine a specific brand asset.
  Trigger phrases: "generate a logo", "make me a logo", "generate color palette",
  "refine the palette", "new typography", "generate brand names", "suggest names for my brand",
  "generate website UI", "create landing page design", "regenerate the logo",
  "I want a different color palette", "refine my logo", "try a different logo style",
  "generate all logos", "show me logo options". Also use for any publishing action:
  "publish this palette", "publish the logo", "make this the active brand name".
metadata:
  version: "0.2.0"
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
| `generate_logo` | Generate a logo image in one of 6 styles using Gemini |
| `get_logo` | Get a specific logo version by ID (includes image_url + concept) |
| `list_logos` | List all logo versions (filter by style/status) |
| `publish_logo` | Publish a logo version |
| `upload_primary_logo` | Upload/replace the primary logo reference image |
| `delete_primary_logo` | Remove the primary logo reference image |
| `generate_website_ui` | Generate a landing page hero section UI image |
| `get_website_ui` | Get a specific website UI version by ID |
| `list_website_uis` | List all website UI versions |
| `rate_asset` | Rate any asset as positive/negative (thumbs up/down) |

## Prerequisites

Before generating assets, the brand needs:
- A completed and submitted questionnaire
- A generated brand analysis (Step 3)

For logo and website UI generation, also needed:
- Published color palette (Step 4)
- Published typography (Step 5)

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
