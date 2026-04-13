---
name: brandvoca
description: >
  Master entry point for ALL BrandVoca tasks. Use this skill for every BrandVoca-related
  request without exception — whether the user wants to create a brand, generate
  a logo or color palette, check credits, manage their account, or anything else BrandVoca-
  related. This skill acts as an intelligent router: it reads the user's intent, picks the
  right BrandVoca sub-skill, reads it, and executes it fully.

  Trigger on any mention of: BrandVoca, brand creation, brand identity, logo generation,
  color palette, typography, brand names, website UI, brand kit, design system, BrandVoca
  credits, BrandVoca subscription, "create a brand", "build a brand", "what's my balance",
  "my brand project", "generate a logo", "brand workflow", "check domain", "logo SVG".
  When in doubt whether BrandVoca is relevant, use this skill.
metadata:
  version: "2.0.0"
---

# BrandVoca — Unified Skill Router

You are handling a BrandVoca request. Your job is a two-step process: **decide** which
sub-skill applies, then **read it and follow it completely**. Do not try to work from memory —
always read the sub-skill file before calling any BrandVoca tools.

> **Authentication**: BrandVoca uses JWT tokens set via `BRANDVOCA_API_KEY` in the environment.
> No login step is needed. Just start using the tools. If a tool returns a 401 error, read
> `../login/SKILL.md` for token refresh instructions.

---

## Step 1 — Route to the Right Sub-Skill

Think through what the user is actually trying to accomplish, then pick exactly one sub-skill
from the table below. Read that file and follow its instructions.

### Full Brand Workflow → read `../brand-workflow/SKILL.md`

Use when the user:
- Wants to create a brand from scratch or start a new brand project
- Asks "what should I do next?" or "where am I in the process?"
- Wants a guided walk-through of the complete brand creation pipeline
- Has a brand that's incomplete and needs to know which step comes next
- Mentions "brand intake", "questionnaire", "brand analysis", or asks about pipeline status

### Generate / Refine / Publish Brand Assets → read `../brand-assets/SKILL.md`

Use when the user:
- Wants to generate a specific asset — logo, color palette, typography, brand names,
  website UI, or brand kit
- Wants to refine, regenerate, or try a different version of an existing asset
- Wants to publish an asset version they're happy with
- Already has a brand and is working on individual pieces (not starting from scratch)
- Asks about domain availability, logo SVG export, or setting a logo as primary
- Says things like "make me a logo", "try a different palette", "generate brand names",
  "check if this domain is available", "export logo as SVG", "set this as my primary logo"

### Account, Credits & Billing → read `../account-management/SKILL.md`

Use when the user:
- Asks about credits, balance, or how much a generation costs
- Wants to check, upgrade, or compare subscription plans (Free / Pro / Max)
- Wants to buy credit packs or top up their balance
- Asks about payment history or transaction records
- Wants to update their profile (name, email)
- Gets a 402 error (insufficient credits) or 403 error (brand limit reached)

### Authentication Error → read `../login/SKILL.md`

Use only when:
- A tool returns a 401 Unauthorized error
- The user explicitly says "I'm getting an authentication error" or "my token expired"

---

## Step 2 — Read the Sub-Skill and Follow It

Once you've picked the right sub-skill, use the Read tool to open the file and read it
fully before taking any action. The sub-skill contains the authoritative instructions —
which tools to call, what to show the user, how to handle errors, and how to present results.

**Sub-skill paths (relative to this file):**

| Sub-Skill | Path | What it covers |
|-----------|------|----------------|
| Brand Workflow | `../brand-workflow/SKILL.md` | Full 9-step brand pipeline, new brand creation, status checks |
| Brand Assets | `../brand-assets/SKILL.md` | Generate/refine/publish logos, palettes, typography, UI, brand kit, domain check, SVG |
| Account Management | `../account-management/SKILL.md` | Credits, billing, plans, profile, error recovery |
| Auth Error | `../login/SKILL.md` | Token refresh, 401 error handling |

---

## Handling Ambiguous Requests

When a request could fit multiple sub-skills, use this priority order:

1. **Error recovery first** — if a tool returned a 402 or 403 error, switch to account-management immediately.
2. **Most specific match wins** — "generate a logo for my existing brand" → brand-assets, even though brand-workflow also mentions logos.
3. **New users → workflow** — if the user is clearly just getting started or asks "where do I begin", use brand-workflow.
4. **When unsure → ask** — a quick "Are you looking to start a new brand, or work on an asset for an existing one?" is always better than guessing wrong.

---

## Example Routing Decisions

| User says | Route to |
|-----------|----------|
| "I want to start a new brand for my coffee shop" | brand-workflow |
| "Generate a flat vector logo for my brand" | brand-assets |
| "How many credits do I have left?" | account-management |
| "What step is my brand on?" | brand-workflow |
| "Refine the color palette — it feels too cold" | brand-assets |
| "What does the Pro plan include?" | account-management |
| "I got an error: not authenticated" | login |
| "Create a brand kit for my brand" | brand-assets |
| "Walk me through creating my brand identity" | brand-workflow |
| "Buy me the Creator credit pack" | account-management |
| "Check if brandvoca.com is available" | brand-assets |
| "Export my logo as SVG" | brand-assets |
| "Set this logo as my primary reference" | brand-assets |
