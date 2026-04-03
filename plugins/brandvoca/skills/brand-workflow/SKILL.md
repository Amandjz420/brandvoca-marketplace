---
name: brandvoca-brand-workflow
description: >
  Use this skill when the user says "set up a new brand", "create a brand from scratch",
  "walk me through brand creation", "build a brand identity", "start a new brand project",
  "what's the status of my brand", or wants to understand the complete BrandVoca pipeline
  end-to-end. Also use when the user asks "what should I do next" for a brand that already
  exists but is incomplete.
metadata:
  version: "0.2.0"
---

# BrandVoca Brand Workflow

Guide the user through BrandVoca's 8-step brand identity pipeline. Each step builds on the previous one.

## Available Tools (Workflow-Specific)

| Tool | What it does |
|------|-------------|
| `brand_intake` | Create a new brand from text + file uploads; Gemini auto-fills questionnaire |
| `get_brand` | Get full brand details to check pipeline status |
| `get_questionnaire` | View the 30-field questionnaire and its completion status |
| `update_questionnaire` | Update/submit questionnaire fields (set submit=True to finalize) |
| `generate_brand_analysis` | Generate 7-section brand analysis from completed questionnaire |
| `generate_color_palette` | Generate color system (+ `publish_color_palette`) |
| `generate_typography` | Generate font-pairing system (+ `publish_typography`) |
| `generate_brand_names` | Generate name suggestions (+ `publish_brand_name`) |
| `generate_logo` | Generate logo in one of 6 styles (+ `publish_logo`) |
| `upload_primary_logo` | Upload a reference logo image before generating logos |
| `generate_website_ui` | Generate landing page hero section |

## The Pipeline (in order)

```
1. Intake        → create brand + auto-fill questionnaire
2. Questionnaire → user reviews/completes 30 fields → submit
3. Analysis      → Gemini generates 7-section brand analysis
4. Color Palette → Gemini generates color system (auto-published on first run)
5. Typography    → Gemini generates font-pairing system (auto-published on first run)
6. Brand Name    → Grok generates name suggestions → user picks one to publish
7. Logo          → Gemini generates logo images (6 styles available)
8. Website UI    → Gemini generates landing page hero section
```

## Starting a New Brand

When the user wants to create a brand from scratch:

1. Ask what they have: text description, uploaded files, or both.
2. Explain that the intake step accepts text + documents/images and Gemini will auto-fill the questionnaire.
3. Call `brand_intake(text="...", file_paths="path1,path2")`.
   - `text`: free-form brand description (idea, vision, industry, audience, etc.).
   - `file_paths`: comma-separated local file paths (images, PDFs, docs, presentations). Optional.
   - Accepted files: .jpg, .jpeg, .png, .webp, .heic, .heif, .pdf, .docx, .doc, .txt, .pptx, .ppt, .xlsx, .xls (max 50 MB each).
4. The response includes the new `brand_id` and a pre-filled questionnaire (status: `questionnaire_pending`).
5. Proceed to Step 2 — review the questionnaire with the user.

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

### Step 1 — Brand Intake (Creating a New Brand)
- Call `brand_intake(text="...", file_paths="...")` with whatever the user provides.
- The response includes the `brand_id` and a questionnaire pre-filled by Gemini.
- Show the user which fields were auto-filled and which are still empty.
- Proceed to Step 2.

### Step 2 — Questionnaire Review & Submission
- Call `get_questionnaire(brand_id)` to see all 30 fields and their current values.
- Walk through the fields with the user, focusing on any that are empty or need correction.
- Key required fields for submission: `brand_name`, `tagline`, `one_sentence_description`, `industry_category`, `primary_target_audience`, `secondary_target_audience`, `why_these_audiences`, `problem_solved`, `core_promise`, `differentiators`, `brand_emotion`, `price_quality_spectrum`, `logo_works_small`, `preferred_logo_type`, `modern_classic` (1-10), `minimal_detailed` (1-10), `playful_serious` (1-10), `soft_sharp` (1-10), `human_techy` (1-10), `friendly_professional` (1-10), `brand_values` (3-7 items), `main_use_cases`.
- To save changes without submitting: call `update_questionnaire(brand_id, field1="...", field2="...")`.
- To finalize and submit: call `update_questionnaire(brand_id, submit=True, ...)` with any remaining field updates.
- After submission, the brand status changes to `questionnaire_completed` and Step 3 becomes available.

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
- **Optional**: If the user has an existing logo they want to use as a reference, call `upload_primary_logo(brand_id, file_path="...")` before generating. This gives Gemini a visual reference. To remove it later, call `delete_primary_logo(brand_id)`.
- Explain there are 6 styles available. Ask which the user wants to generate.
- Call `generate_logo(brand_id, style="...")` — this will take 20–60 seconds.
- Show the returned `image_url` and `concept` text.
- To view a specific version later: `get_logo(brand_id, logo_id)`.
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
