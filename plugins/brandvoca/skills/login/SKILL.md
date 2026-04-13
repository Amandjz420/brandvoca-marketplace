---
name: brandvoca-auth
description: >
  BrandVoca authentication reference. The MCP server uses JWT tokens set via
  BRANDVOCA_API_KEY — no in-session login is needed. Use ONLY when a tool
  returns a 401 Unauthorized error or the user explicitly mentions a token error.
metadata:
  version: "1.0.0"
---

# BrandVoca Authentication

BrandVoca handles authentication via JWT tokens set in the environment. No login
step is required during a conversation.

## How Authentication Works

The BrandVoca MCP server authenticates every request using the `BRANDVOCA_API_KEY`
environment variable, which is the JWT access token from the BrandVoca web or
mobile app. This token is set once when the plugin is installed and remains
valid across sessions.

**The user does not need to log in — just use the BrandVoca tools directly.**

## If You See a 401 or Authentication Error

A 401 error means the token has expired or is invalid:

1. Ask the user to open the BrandVoca app or website and copy a fresh access token.
2. Advise them to update `BRANDVOCA_API_KEY` in their Claude plugin settings.
3. Once updated, all tools will work again.

## Checking Your Account

To see profile, credits, and plan — call `get_my_profile()`. This confirms
the token is valid and shows the current account status.

## Updating Profile Details

To update name or email: call `update_profile(email="...", first_name="...", last_name="...")`.
Only pass the fields you want to change.
