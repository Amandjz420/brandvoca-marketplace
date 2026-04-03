---
name: brandvoca
description: >
  Master entry point for ALL BrandVoca tasks. Use this skill for every BrandVoca-related
  request without exception — whether the user wants to log in, create a brand, generate
  a logo or color palette, check credits, manage their account, or anything else BrandVoca-
  related. This skill acts as an intelligent router: it reads the user's intent, picks the
  right BrandVoca sub-skill, reads it, and executes it fully.

  Trigger on any mention of: BrandVoca, brand creation, brand identity, logo generation,
  color palette, typography, brand names, website UI, brand kit, design system, BrandVoca
  credits, BrandVoca subscription, login to BrandVoca, sign up for BrandVoca, "create a
  brand", "build a brand", "what's my balance", "my brand project", "generate a logo",
  "brand workflow". When in doubt whether BrandVoca is relevant, use this skill.
metadata:
  version: "1.0.0"
---

# BrandVoca — Unified Skill Router

You are handling a BrandVoca request. Your job is a two-step process: **decide** which
sub-skill applies, then **read it and follow it completely**. Do not try to work from memory —
always read the sub-skill file before calling any BrandVoca tools.

---

## Step 1 — Check Authentication

Before calling any BrandVoca tool, confirm the user is authenticated. If `BRANDVOCA_API_KEY`
is not set in the environment and no login has happened in this session, authentication must
come first — even if the user's request is about something else entirely.

If authentication is needed → read `../login/SKILL.md` and follow it, then come back and
continue with the user's original request.

---

## Step 2 — Route to the Right Sub-Skill

Think through what the user is actually trying to accomplish, then pick exactly one sub-skill
from the table below. Read that file and follow its instructions.

### Login / Authentication → read `../login/SKILL.md`

Use when the user:
- Wants to log in, sign in, sign up, register, or log out
- Gets a "Not authenticated" or 401 error from any BrandVoca tool
- Mentions connecting their account or setting up a BrandVoca API key
- Wants to create an account or reset their session

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
- Says things like "make me a logo", "try a different palette", "generate brand names",
  "I want a more minimal logo style", "publish this palette"

### Account, Credits & Billing → read `../account-management/SKILL.md`

Use when the user:
- Asks about credits, balance, or how much a generation costs
- Wants to check, upgrade, or compare subscription plans (Free / Pro / Max)
- Wants to buy credit packs or top up their balance
- Asks about payment history or transaction records
- Wants to update their profile (name, email)
- Gets a 402 error (insufficient credits) or 403 error (brand limit reached)

---

## Step 3 — Read the Sub-Skill and Follow It

Once you've picked the right sub-skill, use the Read tool to open the file and read it
fully before taking any action. The sub-skill contains the authoritative instructions —
which tools to call, what to show the user, how to handle errors, and how to present results.

**Sub-skill paths (relative to this file):**

| Sub-Skill | Path | What it covers |
|-----------|------|----------------|
| Login | `../login/SKILL.md` | Auth, register, logout, token refresh, session setup |
| Brand Workflow | `../brand-workflow/SKILL.md` | Full 9-step brand pipeline, new brand creation, status checks |
| Brand Assets | `../brand-assets/SKILL.md` | Generate/refine/publish logos, palettes, typography, UI, brand kit |
| Account Management | `../account-management/SKILL.md` | Credits, billing, plans, profile, error recovery |

---

## Handling Ambiguous Requests

When a request could fit multiple sub-skills, use this priority order:

1. **Authentication first** — if the user isn't logged in, always handle that before anything else.
2. **Error recovery next** — if a tool returned a 402 or 403 error, switch to account-management immediately.
3. **Most specific match wins** — "generate a logo for my existing brand" → brand-assets, even though brand-workflow also mentions logos.
4. **New users → workflow** — if the user is clearly just getting started or asks "where do I begin", use brand-workflow to give them the full guided experience.
5. **When unsure → ask** — a quick "Are you looking to start a new brand, or work on an asset for an existing one?" is always better than guessing wrong.

---

## Example Routing Decisions

| User says | Route to |
|-----------|----------|
| "I want to start a new brand for my coffee shop" | brand-workflow |
| "Generate a flat vector logo for my brand" | brand-assets |
| "How many credits do I have left?" | account-management |
| "Sign me in to BrandVoca" | login |
| "What step is my brand on?" | brand-workflow |
| "Refine the color palette — it feels too cold" | brand-assets |
| "What does the Pro plan include?" | account-management |
| "I got an error: not authenticated" | login |
| "Create a brand kit for my brand" | brand-assets |
| "Walk me through creating my brand identity" | brand-workflow |
| "Buy me the Creator credit pack" | account-management |
