---
name: login
description: >
  Use this skill at the START of every BrandVoca session before calling any
  other tool. Trigger when: the user hasn't logged in yet, any tool returns
  "Not authenticated", the user says "login", "sign in", "connect my account",
  "use my BrandVoca account", or when BRANDVOCA_API_KEY is not set in the
  environment. Also trigger for "login with Google", "sign in with Apple".
metadata:
  version: "0.1.0"
---

# BrandVoca Login

Authenticate the user before any other BrandVoca tool can be used.

## When to Trigger This Skill

- **First message of a session** — if BRANDVOCA_API_KEY is not set, always ask the user to authenticate before doing anything else.
- **Any tool returns this error**: `"Not authenticated. Call the login tool first, or set BRANDVOCA_API_KEY in your environment."` — immediately run this skill.
- **User says**: "login", "sign in", "connect my account", "I want to use BrandVoca", "use my account".

## Authentication Methods

### Option A — Environment Variable (recommended, persistent)
If the user has already set `BRANDVOCA_API_KEY` in their environment, all tools work immediately. No login call needed. Confirm with: "Your BrandVoca API key is configured — you're ready to go."

### Option B — Email + Password Login (runtime, this session only)
1. Ask: "What's your BrandVoca username and password?"
2. Call `login(username="...", password="...")`.
3. On success: "You're logged in as [username]. Your session is active for this conversation."
4. On failure: show the error and ask them to try again or reset their password via the web app.

### Option C — Google Sign-In
1. Ask: "What's the email address on your Google account?"
2. Optionally ask for first/last name (improves the profile).
3. Call `login_with_google(email="...", first_name="...", last_name="...")`.
4. On success: report credits and subscription plan.

### Option D — Apple Sign-In
1. Ask: "What's the email address on your Apple account?"
2. Note: Apple only sends the name on the very first sign-in — it's fine to skip if the user doesn't know.
3. Call `login_with_apple(email="...", first_name="...", last_name="...")`.
4. On success: report credits and subscription plan.

## After Successful Login

Always immediately call `get_my_profile()` and report back:

```
✅ Logged in as [username]
💳 Credits: [balance]
📋 Plan: [plan name] ([credits_per_month] credits/month)
🏷️ Brands: [max_brands == 0 ? "Unlimited" : max_brands]
```

Then ask: "What would you like to do? I can help you create a brand, generate assets, or check your account."

## Session Scope

The token is stored **in memory for this conversation only**. When the conversation ends, the token is gone. The user will need to log in again next session unless they set `BRANDVOCA_API_KEY` as a persistent environment variable.

To set it permanently:
```bash
# Add to ~/.zshrc or ~/.bashrc
export BRANDVOCA_API_KEY="paste_your_access_token_here"
```

The access token from a successful login response can be used as the API key value.

## Error Handling

| Error | Action |
|-------|--------|
| `Login failed: ...` | Show the error, ask to retry or check credentials |
| Wrong password | Suggest resetting password at the BrandVoca web app |
| Account not found | Offer to sign up via the web app at brandvoca.ai |
| Network error | Check if the BrandVoca backend is reachable |
