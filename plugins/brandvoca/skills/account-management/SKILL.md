---
name: brandvoca-account-management
description: >
  Use this skill when the user asks about their credits, balance, subscription, plan,
  pricing, transaction history, usage, profile, account, or billing. Also use when the
  user says "how many credits do I have", "what plan am I on", "show my usage",
  "check my balance", "upgrade my plan", "what does this cost", "how much will it cost
  to generate a logo", "show my transactions", "view my profile", "edit my profile",
  "buy credits", "top up credits", "show credit packs", or "what's included in the Pro plan".
  Also trigger proactively when a generation returns a 402 (insufficient credits) or
  403 (brand limit reached) error.
metadata:
  version: "0.3.0"
---

# BrandVoca Account Management

Help users manage their account: check credits, view subscription plans, review transaction
and payment history, estimate generation costs, buy credit packs, and handle credit/limit errors.

## Available Tools

| Tool | What it does |
|------|-------------|
| `get_my_profile` | Full profile: name, email, credit balance, current subscription, recent payments |
| `update_profile` | Update user's email, first name, or last name |
| `get_credit_balance` | Quick credit balance check (lightweight) |
| `get_credit_transactions` | Paginated transaction history with filters |
| `get_model_pricing` | Credit cost per action — for estimating before generating |
| `get_subscription_plans` | All plans: Free, Pro, Max with INR pricing (public, no auth needed) |
| `get_my_subscription` | Current plan details, status, billing period, balance, recent payments |
| `get_credit_packs` | List purchasable one-time credit bundles (Starter / Creator / Pro Pack) |
| `create_payment_order` | Create a Razorpay order for subscription upgrade or credit top-up |
| `verify_payment` | Verify & capture a Razorpay payment after checkout |
| `get_payment_history` | Full payment history: subscriptions and credit top-ups |

## Common Scenarios

### "How many credits do I have?"

1. Call `get_credit_balance()`.
2. Report clearly: "You have **485 credits** remaining."
3. If low (below 50), proactively mention: "That's getting low — a full brand workflow costs about 200 credits. You might want to top up or upgrade your plan."

### "What plan am I on?"

1. Call `get_my_subscription()`.
2. Report: plan name, monthly credits, brand limit, status, billing period end.
3. Example: "You're on the **Free** plan — 500 credits/month, 1 brand project, status: active."

### "Show me the available plans" / "What are the pricing options?"

1. Call `get_subscription_plans()`.
2. Present all plans clearly:

```
**Free** — ₹0/mo
  500 credits • 1 brand project • Community support

**Pro** — ₹499/mo ⭐ Most Popular
  5,000 credits • Unlimited brands • Priority support • Brand asset exports

**Max** — ₹999/mo
  20,000 credits • Unlimited brands • Dedicated support • API access • Team collaboration
```

3. If you know their current plan, highlight it and suggest the logical upgrade.
4. Payments can be initiated via `create_payment_order` and completed via `verify_payment` (Razorpay flow), or the user can upgrade through the BrandVoca web app.

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
| Logo Generation | ~40 |
| Website UI | ~50 |
| **Full workflow** | **~200** |

4. Compare against their balance: "A logo costs about 40 credits. You have 485, so you're good."

### "Show my transaction history" / "What have I spent credits on?"

1. Call `get_credit_transactions(limit=20)`.
2. Present as a clean list, most recent first:

```
• Apr 3, 12:30 — Logo Generation        — -40 credits  (balance: 485)
• Apr 3, 12:15 — Brand Name             — -30 credits  (balance: 525)
• Apr 3, 00:00 — Plan upgrade to Pro    — +4,515 credits (balance: 5,000)
• Mar 28, 00:00 — Sign-up Bonus         — +500 credits  (balance: 500)
```

3. Use `+` for credits added (green), `-` for credits used (red).
4. Filtering options: `get_credit_transactions(action="logo_generation")` or `get_credit_transactions(transaction_type="usage")`.

### "Buy credits" / "Top up my credits" / "Show credit packs"

1. Call `get_credit_packs()`.
2. Present the available one-time credit bundles:

```
**Starter Pack** — ₹99
  500 credits • Perfect for trying out extra generations

**Creator Pack** — ₹299 ⭐ Most Popular
  2,000 credits • Great for ongoing brand work

**Pro Pack** — ₹799
  6,000 credits • Best value for power users
```

3. If the user wants to purchase directly, use the payment flow:
   a. Call `create_payment_order(amount=<paise>, payment_type="credit_topup", credit_pack_id="<pack_uuid>")`.
      - Amount is in paise (e.g. ₹299 = 29900 paise).
   b. The response contains `order_id`, `amount`, `currency`, and `key_id`.
   c. The user completes checkout via Razorpay (web app or frontend handles the UI).
   d. After checkout, call `verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature, payment_type="credit_topup", credit_pack_id="<pack_uuid>")`.
   e. On success: credits are added immediately. Report the new balance.
4. Alternatively, direct the user to the BrandVoca web app to complete the purchase.

### "Upgrade my plan" / "Switch to Pro"

1. Call `get_subscription_plans()` to show options.
2. Call `get_my_subscription()` to show their current plan.
3. If the user confirms an upgrade:
   a. Call `create_payment_order(amount=<paise>, payment_type="subscription", plan_id="<plan_uuid>")`.
   b. The user completes checkout via Razorpay.
   c. Call `verify_payment(...)` with `payment_type="subscription"` and `plan_id`.
   d. On success: subscription is upgraded immediately. Report the new plan and credit balance.

### "Show my payment history" / "What have I paid for?"

1. Call `get_payment_history()`.
2. Present as a table:

```
• Apr 3  — Subscription (Pro)     — ₹499   — completed
• Apr 3  — Credit Top-up (Creator)— ₹299   — completed
```

### "Edit my profile" / "Update my name" / "Change my email"

1. Ask which fields to update: email, first name, or last name.
2. Call `update_profile(email="...", first_name="...", last_name="...")` — only pass the fields being changed.
3. On success: confirm the update and show the new profile info.
4. On failure: show the error (e.g. email already taken).

## Proactive Credit Awareness

**Before expensive operations**: Before any logo or website UI generation (40–50 credits each), check balance first:

1. Call `get_credit_balance()`.
2. If balance < estimated cost, warn BEFORE calling the generation tool.
3. Example: "Heads up — website UI costs ~50 credits and you only have 35. Want to top up first, or proceed anyway?"

**After 402 errors** (insufficient credits):
1. Call `get_credit_balance()` to confirm balance.
2. Call `get_model_pricing()` to show the action cost.
3. Call `get_credit_packs()` to show top-up options.
4. Call `get_subscription_plans()` to show upgrade options.
5. Present clearly: "You need ~40 credits but only have 12. Here are your options: [show packs + plans]."

**After 403 errors** (brand limit):
1. Call `get_my_subscription()` to check `max_brands`.
2. Explain: "Your Free plan allows 1 brand project. You've reached that limit."
3. Call `get_subscription_plans()` and suggest upgrading to Pro (₹499/mo) or Max (₹999/mo) for unlimited brands.

## Credit Math

Credits are stored as decimals (e.g. "485.00"). When presenting:
- Round to whole numbers: "485 credits" not "485.00 credits"
- For cost estimates, use "approximately" since token-based costs vary slightly
- Flat-cost actions (logo ~40, website UI ~50) are close to exact

## Plan Quick Reference

| | Free | Pro | Max |
|---|---|---|---|
| Price | ₹0/mo | ₹499/mo | ₹999/mo |
| Credits | 500/mo | 5,000/mo | 20,000/mo |
| Brands | 1 | Unlimited | Unlimited |
| Full workflows | ~2 | ~25 | ~100 |
