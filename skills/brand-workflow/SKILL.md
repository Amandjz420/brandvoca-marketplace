---
name: brand-workflow
description: >
  Use this skill when the user says "set up a new brand", "create a brand from scratch",
  "walk me through brand creation", "build a brand identity", "start a new brand project",
  "what's the status of my brand", or wants to understand the complete BrandVoca pipeline
  end-to-end. Also use when the user asks "what should I do next" for a brand that already
  exists but is incomplete.
metadata:
  version: "0.1.0"
---

# BrandVoca Brand Workflow

Guide the user through BrandVoca's 7-step brand identity pipeline. Each step builds on the previous one.

## The Pipeline (in order)

```
1. Intake       → create brand + auto-fill questionnaire
2. Questionnaire → user reviews/completes 30 fields
3. Analysis      → Gemini generates 7-section brand analysis
4. Color Palette → Gemini generates color system (auto-published on first run)
5. Typography   → Gemini generates font-pairing system (auto-published on first run)
6. Brand Name   → Grok generates name suggestions → user picks one to publish
7. Logo         → Gemini generates logo images (6 styles available)
8. Website UI   → Gemini generates landing page hero section
```

## Starting a New Brand

When the user wants to create a brand from scratch:

1. Ask what they have: text description, uploaded files, or both.
2. Explain that the intake step accepts text + documents/images and Gemini will auto-fill the questionnaire.
3. Use the BrandVoca frontend for intake (it accepts file uploads). The API intake endpoint only takes text + file paths server-side, so direct the user to the web app for intake.
4. Once the brand_id is known, proceed with the pipeline using the MCP tools.

## Checking What Step a Brand Is On

Call `get_brand(brand_id)` and inspect the response:

- `status: "questionnaire_pending"` → questionnaire exists but not submitted
- `status: "questionnaire_completed"` → ready to generate analysis
- `status: "analysis_completed"` → ready to generate palette/typography
- `analysis` is present → Step 3 done
- `published_color_palette` is present → Step 4 done
- `published_typography` is present → Step 5 done
- `published_brand_name.name` is present → Step 6 done
- `published_logos` is non-empty → Step 7 done
- `latest_website_ui` is present → Step 8 done

Tell the user clearly which step they're on and what comes next.

## Guiding Through Each Step

### Step 3 — Brand Analysis
- Call `generate_brand_analysis(brand_id)`.
- Present the `brand_summary` field to the user in a readable way.
- Mention that the full analysis (values, personality, visual do's/don'ts) is now available and drives all subsequent generation.

### Step 4 — Color Palette
- Call `generate_color_palette(brand_id)`.
- Show the `core_palette` colors (name + hex) in a clean list.
- Show `color_rationale_summary`.
- First generation is auto-published.
- If the user wants changes: call `generate_color_palette(brand_id, user_feedback="...", previous_version_id="...")` then `publish_color_palette(brand_id, palette_id)` on the new version.

### Step 5 — Typography
- Call `generate_typography(brand_id)`.
- Show the primary and secondary typefaces with style descriptions.
- Show `font_pairing_rationale`.
- Same draft/publish flow as color palette.

### Step 6 — Brand Name
- Call `generate_brand_names(brand_id)`.
- Present the 5 categories of suggestions clearly: Descriptive, Invented, Compound, Metaphorical, Abbreviations.
- Ask the user to pick a name they like.
- Call `publish_brand_name(brand_id, name_id, name="chosen name")`.
- Confirm that the name is now propagated across all existing brand assets.

### Step 7 — Logo
- Explain there are 6 styles available. Ask which the user wants to generate.
- Call `generate_logo(brand_id, style="...")` — this will take 20–60 seconds.
- Show the returned `image_url` and `concept` text.
- Suggest trying multiple styles: flat_vector first (most versatile), then geometric_minimal.
- For refinement: call `generate_logo` with `user_feedback` + `previous_version_id`.

### Step 8 — Website UI
- Call `generate_website_ui(brand_id)` — takes 20–60 seconds.
- Show the returned `image_url` and `concept` text.
- Explain this is a 1440px desktop landing page hero section: nav bar, hero headline, visual system element.
- For refinement: call `generate_website_ui` with `user_feedback` + `previous_version_id`.

## Presenting Results

- Always show image URLs as markdown links: `[View Logo](https://...)`.
- For color palettes: show hex codes as inline code blocks `#1A2B3C`.
- For typography: show font names in bold.
- Keep responses focused — don't dump the entire JSON. Extract the key information.
- After each generation step, ask: "Happy with this, or would you like to refine it?"
