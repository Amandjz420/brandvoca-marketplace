---
name: account-management
description: >
  Use this skill when the user asks about their credits, balance, subscription, plan,
  pricing, transaction history, usage, profile, account, or billing. Also use when the
  user says "how many credits do I have", "what plan am I on", "show my usage",
  "check my balance", "upgrade my plan", "what does this cost", "how much will it cost
  to generate a logo", "show my transactions", "view my profile", "edit my profile",
  or "what's included in the Pro plan". Also trigger proactively when a generation
  returns a 402 (insufficient credits) or 403 (brand limit reached) error.
metadata:
  version: "0.1.0"
---

# BrandVoca Account Management

Help users manage their account: check credits, view subscription plans, review transaction history, estimate generation costs, and handle credit/limit errors.

## Available Tools

| Tool | What it does |
|------|-------------|
| `get_my_profile` | Full profile: name, email, credit balance, current subscription |
| `get_credit_balance` | Quick credit balance check (lightweight) |
| `get_credit_transactions` | Paginated transaction history with filters |
| `get_model_pricing` | Credit cost per action — for estimating before generating |
| `get_subscription_plans` | All plans: Free, Pro, Max (public, no auth needed) |
| `get_my_subscription` | Current plan details, status, billing period, balance |

## Common Scenarios

### "How many credits do I have?"

1. Call `get_credit_balance()`.
2. Report the number clearly: "You have **485 credits** remaining."
3. If low (below 50), proactively mention: "That's getting low — a full brand workflow costs about 200 credits. You might want to consider upgrading your plan."

### "What plan am I on?"

1. Call `get_my_subscription()`.
2. Report: plan name, monthly credits, brand limit, status.
3. Example: "You're on the **Free** plan — 500 credits/month, 1 brand project, status: active."

### "Show me the available plans" / "What are the pricing options?"

1. Call `get_subscription_plans()`.
2. Present all plans in a clear comparison:

```
**Free** — $0/mo
  500 credits • 1 brand • Community support

**Pro** — $20/mo ⭐ Most Popular
  10,000 credits • Unlimited brands • Priority support

**Max** — $100/mo
  100,000 credits • Unlimited brands • Dedicated support • API access
```

3. If you know their current plan, highlight it and suggest the logical upgrade.

### "How much does it cost to generate X?"

1. Call `get_model_pricing()`.
2. Look up the action and report the approximate cost.
3. Reference table:

| Action | Approx. Credits |
|--------|----------------|
| Intake (create brand) | ~15 |
| Brand Analysis | ~25 |
| Color Palette | ~20 |
| Typography | ~20 |
| Brand Name (Grok) | ~30 |
| Logo Generation | 40 |
| Website UI | 50 |
| **Full workflow** | **~200** |

4. Compare against their balance: "A logo costs about 40 credits. You have 485, so you're good."

### "Show my transaction history" / "What have I spent credits on?"

1. Call `get_credit_transactions(limit=20)`.
2. Present as a clean list, most recent first:

```
• Mar 28, 12:30 — Logo Generation — -40 credits (balance: 485)
• Mar 28, 12:15 — Brand Name — -30 credits (balance: 525)
• Mar 28, 00:00 — Sign-up Bonus — +500 credits (balance: 500)
```

3. Use `+` (green) for credits added, `-` (red) for credits used.
4. If the user wants to filter: `get_credit_transactions(action="logo_generation")` or `get_credit_transactions(transaction_type="usage")`.

### "Edit my profile" / "Update my name"

1. Call `get_my_profile()` to show current values.
2. The profile can be updated via the web app (PATCH /api/auth/me/). The MCP server currently doesn't have an update_profile tool, so direct the user to the web app for edits.

## Proactive Credit Awareness

**Before expensive operations**: When about to run a generation (especially logo or website UI at 40–50 credits each), proactively check the balance first:

1. Call `get_credit_balance()`.
2. If balance < estimated cost, warn the user BEFORE calling the generation tool.
3. Example: "Heads up — a website UI generation costs about 50 credits, and you only have 35 left. Want to proceed, or would you like to check upgrade options first?"

**After 402 errors**: If any generation tool returns a 402 (insufficient credits):

1. Call `get_credit_balance()` to confirm the current balance.
2. Call `get_model_pricing()` to show what the action costs.
3. Call `get_subscription_plans()` to show upgrade options.
4. Present it clearly: "You don't have enough credits for this. You need ~40 credits but only have 12. Here are your upgrade options: [show plans]."

**After 403 errors (brand limit)**: If brand creation returns 403:

1. Call `get_my_subscription()` to check the plan's `max_brands`.
2. Explain: "Your Free plan allows 1 brand project. You've reached that limit."
3. Call `get_subscription_plans()` and suggest upgrading to Pro or Max for unlimited brands.

## Credit Math

Credits are stored as decimals (e.g. "485.00"). When presenting to users:
- Round to whole numbers: "485 credits" not "485.00 credits"
- For cost estimates, use "approximately" since token-based costs vary slightly per call
- Flat-cost actions (logo at 40, website UI at 50) are exact

## Plan Comparison Quick Reference

| | Free | Pro | Max |
|---|---|---|---|
| Price | $0/mo | $20/mo | $100/mo |
| Credits | 500/mo | 10,000/mo | 100,000/mo |
| Brands | 1 | Unlimited | Unlimited |
| Full workflows | ~2 | ~50 | ~500 |
