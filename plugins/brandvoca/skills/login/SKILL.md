---
name: login
description: >
  Use this skill at the START of every BrandVoca session before calling any
  other tool. Trigger when: the user hasn't logged in yet, any tool returns
  "Not authenticated", the user says "login", "sign in", "connect my account",
  "use my BrandVoca account", "create an account", "sign up", "register",
  or when BRANDVOCA_API_KEY is not set in the environment. Also trigger for
  "login with Google", "sign in with Apple", "logout", "sign out", "refresh token".
metadata:
  version: "0.2.0"
---

# BrandVoca Login & Authentication

Authenticate the user before any other BrandVoca tool can be used. Also handles
registration, logout, and token refresh.

## Available Tools

| Tool | What it does |
|------|-------------|
| `register` | Create a new account (username, email, password) — stores token on success |
| `login` | Log in with username + password — stores token for this session |
| `login_with_google` | Sign in/up with Google email (trusted mode) |
| `login_with_apple` | Sign in/up with Apple email (trusted mode) |
| `logout` | Revoke a refresh token and clear the session token |
| `refresh_token` | Exchange a refresh token for a new access token |
| `get_my_profile` | Fetch full profile after login (credits, plan, etc.) |

## When to Trigger This Skill

- **First message of a session** — if BRANDVOCA_API_KEY is not set, always ask the user to authenticate before doing anything else.
- **Any tool returns this error**: `"Not authenticated. Call the login tool first, or set BRANDVOCA_API_KEY in your environment."` — immediately run this skill.
- **User says**: "login", "sign in", "connect my account", "I want to use BrandVoca", "use my account".
- **User says**: "create an account", "sign up", "register" — use the `register` tool.
- **User says**: "logout", "sign out" — use the `logout` tool.
- **Token expired (401 error)** — try `refresh_token` first, then fall back to re-login.

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

### Option E — New Account Registration
1. Ask for: username, email, password.
2. Call `register(username="...", email="...", password="...", password2="...")`.
   - `password2` must match `password`.
   - Optionally include `first_name` and `last_name`.
3. On success: token is stored automatically, report the new account details.
4. On failure: show the error (e.g. username taken, email already registered, password too weak).

## After Successful Login / Registration

Always immediately call `get_my_profile()` and report back:

```
Logged in as [username]
Credits: [balance]
Plan: [plan name] ([credits_per_month] credits/month)
Brands: [max_brands == 0 ? "Unlimited" : max_brands]
```

Then ask: "What would you like to do? I can help you create a brand, generate assets, or check your account."

## Logout

When the user wants to log out:
1. Call `logout(refresh_token="...")`.
   - The refresh token was returned during login. If the user doesn't have it, the session token will expire naturally.
2. On success: "You've been logged out. The session token has been cleared."
3. To log in again, they'll need to use one of the login methods above.

## Token Refresh

When a tool returns a 401 (unauthorized / token expired):
1. If the user has a refresh token, call `refresh_token(refresh="...")`.
2. On success: "Access token refreshed — you're good to continue."
3. On failure: fall back to a full re-login using one of the methods above.

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
| Account not found | Offer to create an account with `register` |
| 401 Unauthorized | Try `refresh_token` first, then re-login if that fails |
| Username/email taken (register) | Suggest logging in instead, or using a different username |
| Network error | Check if the BrandVoca backend is reachable |
