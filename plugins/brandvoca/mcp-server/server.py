#!/usr/bin/env python3
"""
BrandVoca MCP Server
--------------------
Exposes the BrandVoca REST API as tools for Claude.

Authentication — two ways to provide credentials:

  Option A (recommended): set env vars before starting Claude
      export BRANDVOCA_API_KEY="your_access_token"
      export BRANDVOCA_API_URL="https://brandvoca-backend-production.up.railway.app"   # optional

  Option B: call the `login` tool from a conversation
      Claude will call login(username, password) → stores the token
      in memory for the rest of the session.
"""
import os
import httpx
from mcp.server.fastmcp import FastMCP

# ── Config ────────────────────────────────────────────────────────────────

API_URL = os.environ.get("BRANDVOCA_API_URL", "https://brandvoca-backend-production.up.railway.app").rstrip("/")

# Token can come from env var OR be set at runtime by the login() tool
_runtime_token: str = os.environ.get("BRANDVOCA_API_KEY", "")

app = FastMCP("brandvoca")


# ── HTTP helpers ──────────────────────────────────────────────────────────

def _headers() -> dict:
    if not _runtime_token:
        raise RuntimeError(
            "Not authenticated. Call the login tool first, or set "
            "BRANDVOCA_API_KEY in your environment."
        )
    return {
        "Authorization": f"Bearer {_runtime_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ── Auth tools ────────────────────────────────────────────────────────────

@app.tool()
def login(username: str, password: str) -> str:
    """
    Log in to BrandVoca with a username and password.
    Stores the access token in memory for this session.
    You only need to call this once per conversation if BRANDVOCA_API_KEY
    is not set in the environment.

    Args:
        username: Your BrandVoca account username.
        password: Your BrandVoca account password.
    """
    global _runtime_token
    with httpx.Client(timeout=15) as client:
        r = client.post(
            f"{API_URL}/api/auth/login/",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
        )
    data = r.json()
    if r.status_code == 200 and data.get("success"):
        _runtime_token = data["tokens"]["access"]
        user = data.get("user", {})
        return (
            f"Logged in as {user.get('username', username)}. "
            f"Access token stored for this session."
        )
    return f"Login failed: {r.text}"


@app.tool()
def login_with_google(email: str, first_name: str = "", last_name: str = "") -> str:
    """
    Sign in (or sign up) using a Google account.
    Trusted mode — the backend accepts the email directly, no token verification.
    Stores the access token in memory for this session.

    Args:
        email: The user's Google email address (required).
        first_name: User's first name from Google profile.
        last_name: User's last name from Google profile.
    """
    global _runtime_token
    payload: dict = {"email": email}
    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name
    with httpx.Client(timeout=15) as client:
        r = client.post(
            f"{API_URL}/api/auth/social/google/",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
    data = r.json()
    if r.status_code == 200 and data.get("success"):
        _runtime_token = data["tokens"]["access"]
        user = data.get("user", {})
        return (
            f"Signed in with Google as {user.get('email', email)}. "
            f"Credits: {user.get('credit_balance', '?')}. "
            f"Token stored for this session."
        )
    return f"Google sign-in failed: {r.text}"


@app.tool()
def login_with_apple(email: str, first_name: str = "", last_name: str = "") -> str:
    """
    Sign in (or sign up) using an Apple account.
    Trusted mode — the backend accepts the email directly, no token verification.
    Stores the access token in memory for this session.

    Args:
        email: The user's Apple email address (required).
        first_name: User's first name (Apple only sends this on first auth).
        last_name: User's last name.
    """
    global _runtime_token
    payload: dict = {"email": email}
    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name
    with httpx.Client(timeout=15) as client:
        r = client.post(
            f"{API_URL}/api/auth/social/apple/",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
    data = r.json()
    if r.status_code == 200 and data.get("success"):
        _runtime_token = data["tokens"]["access"]
        user = data.get("user", {})
        return (
            f"Signed in with Apple as {user.get('email', email)}. "
            f"Credits: {user.get('credit_balance', '?')}. "
            f"Token stored for this session."
        )
    return f"Apple sign-in failed: {r.text}"


@app.tool()
def get_my_profile() -> str:
    """Return the profile of the currently logged-in user including credit balance and subscription."""
    return _get("/api/auth/me/")


# ═══════════════════════════════════════════════════════════════════════════
# Subscription
# ═══════════════════════════════════════════════════════════════════════════


@app.tool()
def get_subscription_plans() -> str:
    """
    List all available subscription plans (Free, Pro, Max).
    Public endpoint — no authentication required.
    Returns plan names, prices, credit allowances, brand limits, and feature lists.
    """
    # Public endpoint, no auth header needed
    with httpx.Client(timeout=15) as client:
        r = client.get(
            f"{API_URL}/api/auth/subscription/plans/",
            headers={"Accept": "application/json"},
        )
        return r.text


@app.tool()
def get_my_subscription() -> str:
    """
    Get the current user's subscription details including plan info,
    status, billing period, and current credit balance.
    """
    return _get("/api/auth/subscription/")


# ═══════════════════════════════════════════════════════════════════════════
# Credits
# ═══════════════════════════════════════════════════════════════════════════


@app.tool()
def get_credit_balance() -> str:
    """
    Get the current user's credit balance.
    Lightweight endpoint — use this for quick balance checks.
    """
    return _get("/api/auth/credits/balance/")


@app.tool()
def get_credit_transactions(
    action: str = "",
    transaction_type: str = "",
    limit: int = 20,
    offset: int = 0,
) -> str:
    """
    List credit transactions for the current user. Supports filtering and pagination.

    Args:
        action: Filter by pipeline action (e.g. 'brand_analysis', 'logo_generation').
        transaction_type: Filter by type ('usage', 'signup_bonus', 'monthly_refill', 'topup', 'refund', 'admin_adjustment').
        limit: Page size (default 20, max 200).
        offset: Pagination offset.
    """
    params: dict = {"limit": limit, "offset": offset}
    if action:
        params["action"] = action
    if transaction_type:
        params["type"] = transaction_type
    return _get("/api/auth/credits/transactions/", params)


@app.tool()
def get_model_pricing() -> str:
    """
    List all active model pricing configurations.
    Shows the credit cost per action (intake, analysis, palette, typography,
    brand name, logo, website UI) so users can estimate costs before generating.
    """
    return _get("/api/auth/credits/pricing/")


@app.tool()
def get_credit_packs() -> str:
    """
    List all active one-time credit packs available for purchase.
    Public endpoint — no authentication required.
    Returns pack names, credit amounts, prices in INR, and descriptions.

    Available packs (approximate):
      Starter  — 500 credits  @ ₹99
      Creator  — 2,000 credits @ ₹299
      Pro Pack — 6,000 credits @ ₹799
    """
    with httpx.Client(timeout=15) as client:
        r = client.get(
            f"{API_URL}/api/payments/credit-packs/",
            headers={"Accept": "application/json"},
        )
        return r.text


@app.tool()
def get_payment_history(limit: int = 20, offset: int = 0) -> str:
    """
    Get the current user's full payment history — both subscription upgrades
    and one-time credit pack top-ups.

    Args:
        limit: Number of records to return (default 20, max 200).
        offset: Pagination offset.
    """
    return _get("/api/payments/history/", {"limit": limit, "offset": offset})


# ── HTTP helpers ──────────────────────────────────────────────────────────


def _get(path: str, params: dict | None = None) -> str:
    with httpx.Client(timeout=30) as client:
        r = client.get(f"{API_URL}{path}", headers=_headers(), params=params or {})
        return r.text


def _post(path: str, data: dict | None = None) -> str:
    # Longer timeout for AI generation endpoints (can take 30–60 s)
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{API_URL}{path}", headers=_headers(), json=data or {})
        return r.text


def _delete(path: str) -> str:
    with httpx.Client(timeout=30) as client:
        r = client.delete(f"{API_URL}{path}", headers=_headers())
        return r.text


# ═══════════════════════════════════════════════════════════════════════════
# Brand
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def list_brands(search: str = "", status: str = "") -> str:
    """
    List all brands in BrandVoca.

    Args:
        search: Optional text to filter brands by name.
        status: Optional status filter (e.g. 'analysis_completed', 'questionnaire_pending').
    """
    params: dict = {}
    if search:
        params["search"] = search
    if status:
        params["status"] = status
    return _get("/api/brands/", params)


@app.tool()
def get_brand(brand_id: str) -> str:
    """
    Get full details of a brand: questionnaire, analysis, published palette,
    published typography, published logos, primary logo URL, latest website UI.

    Args:
        brand_id: UUID of the brand.
    """
    return _get(f"/api/brands/{brand_id}/")


@app.tool()
def delete_brand(brand_id: str) -> str:
    """
    Permanently delete a brand and ALL related data (analysis, palettes,
    typography, brand names, logos, website UIs, uploaded files).

    Args:
        brand_id: UUID of the brand to delete.
    """
    return _delete(f"/api/brands/{brand_id}/")


# ═══════════════════════════════════════════════════════════════════════════
# Questionnaire & Analysis
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def get_questionnaire(brand_id: str) -> str:
    """
    Get the brand questionnaire — shows all 30 fields including which ones
    were auto-filled by Gemini during intake and which are still empty.

    Args:
        brand_id: UUID of the brand.
    """
    return _get(f"/api/brands/{brand_id}/questionnaire/")


@app.tool()
def generate_brand_analysis(brand_id: str) -> str:
    """
    Generate the full 7-section brand analysis from the completed questionnaire
    using Gemini. Produces: brand summary, core value system, personality profile,
    visual dos/don'ts, symbolic direction, brand positioning, creative constraints.

    Requires the questionnaire to be fully submitted first.

    Args:
        brand_id: UUID of the brand.
    """
    return _post(f"/api/brands/{brand_id}/analyze/")


# ═══════════════════════════════════════════════════════════════════════════
# Color Palette
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def generate_color_palette(
    brand_id: str,
    user_feedback: str = "",
    previous_version_id: str = "",
) -> str:
    """
    Generate a new color palette for a brand using Gemini.
    The first generation is automatically published.
    Subsequent generations create drafts — use publish_color_palette to publish.

    For refinement, pass user_feedback and previous_version_id together.

    Args:
        brand_id: UUID of the brand.
        user_feedback: Refinement instructions (e.g. "make it warmer and more earthy").
        previous_version_id: UUID of the palette version to refine from.
    """
    payload: dict = {}
    if user_feedback:
        payload["user_feedback"] = user_feedback
    if previous_version_id:
        payload["previous_version_id"] = previous_version_id
    return _post(f"/api/brands/{brand_id}/color-palette/generate/", payload)


@app.tool()
def list_color_palettes(brand_id: str) -> str:
    """
    List all color palette versions for a brand (draft and published).

    Args:
        brand_id: UUID of the brand.
    """
    return _get(f"/api/brands/{brand_id}/color-palettes/")


@app.tool()
def publish_color_palette(brand_id: str, palette_id: str) -> str:
    """
    Publish a specific color palette version. Automatically unpublishes
    any previously published palette for this brand.

    Args:
        brand_id: UUID of the brand.
        palette_id: UUID of the palette version to publish.
    """
    return _post(f"/api/brands/{brand_id}/color-palette/{palette_id}/publish/")


# ═══════════════════════════════════════════════════════════════════════════
# Typography
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def generate_typography(
    brand_id: str,
    user_feedback: str = "",
    previous_version_id: str = "",
) -> str:
    """
    Generate a typography / font-pairing system for a brand using Gemini.
    The first generation is automatically published.
    Subsequent generations create drafts.

    Args:
        brand_id: UUID of the brand.
        user_feedback: Refinement instructions (e.g. "use only Google Fonts, more geometric").
        previous_version_id: UUID of the typography version to refine from.
    """
    payload: dict = {}
    if user_feedback:
        payload["user_feedback"] = user_feedback
    if previous_version_id:
        payload["previous_version_id"] = previous_version_id
    return _post(f"/api/brands/{brand_id}/typography/generate/", payload)


@app.tool()
def list_typographies(brand_id: str) -> str:
    """
    List all typography versions for a brand.

    Args:
        brand_id: UUID of the brand.
    """
    return _get(f"/api/brands/{brand_id}/typographies/")


@app.tool()
def publish_typography(brand_id: str, typography_id: str) -> str:
    """
    Publish a specific typography version.

    Args:
        brand_id: UUID of the brand.
        typography_id: UUID of the typography version to publish.
    """
    return _post(f"/api/brands/{brand_id}/typography/{typography_id}/publish/")


# ═══════════════════════════════════════════════════════════════════════════
# Brand Name
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def generate_brand_names(
    brand_id: str,
    user_feedback: str = "",
    previous_version_id: str = "",
) -> str:
    """
    Generate AI brand name suggestions using Grok. Returns 5 categories:
    descriptive, invented/abstract, compound, metaphorical, abbreviations.
    Each category has multiple options with rationale.

    Args:
        brand_id: UUID of the brand.
        user_feedback: Direction for the names (e.g. "short, punchy, tech-sounding").
        previous_version_id: UUID of a previous name version to refine from.
    """
    payload: dict = {}
    if user_feedback:
        payload["user_feedback"] = user_feedback
    if previous_version_id:
        payload["previous_version_id"] = previous_version_id
    return _post(f"/api/brands/{brand_id}/brand-name/generate/", payload)


@app.tool()
def list_brand_names(brand_id: str) -> str:
    """
    List all brand name versions for a brand.

    Args:
        brand_id: UUID of the brand.
    """
    return _get(f"/api/brands/{brand_id}/brand-names/")


@app.tool()
def publish_brand_name(brand_id: str, name_id: str, name: str = "") -> str:
    """
    Publish a brand name version. Optionally pick a specific name from the
    AI suggestions. When published, the name is propagated across all brand
    assets (analysis, palettes, typography, logos) automatically.

    Args:
        brand_id: UUID of the brand.
        name_id: UUID of the brand name version to publish.
        name: The specific name string to set as active (optional).
    """
    payload: dict = {}
    if name:
        payload["name"] = name
    return _post(f"/api/brands/{brand_id}/brand-name/{name_id}/publish/", payload)


# ═══════════════════════════════════════════════════════════════════════════
# Logo
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def generate_logo(
    brand_id: str,
    style: str,
    user_feedback: str = "",
    previous_version_id: str = "",
) -> str:
    """
    Generate a logo image for a brand using Gemini image generation.
    Uses the published color palette, typography, and primary logo (if uploaded) as inputs.
    The first generation per style is auto-published.

    Available styles:
      flat_vector        — Clean flat vector logo (3 versions: horizontal, symbol-only, stacked)
      geometric_minimal  — Geometric minimal mark using simple mathematical forms
      abstract_symbolic  — Abstract symbolic mark from brand values
      bold_wordmark      — Modern typography-first wordmark
      minimal_mascot     — Shape-based minimal mascot mark
      dynamic_motion     — Motion-inspired directional geometry mark

    Args:
        brand_id: UUID of the brand.
        style: One of the 6 logo styles listed above.
        user_feedback: Refinement instructions (e.g. "make the symbol more circular").
        previous_version_id: UUID of a previous logo version to refine from.
    """
    payload: dict = {"style": style}
    if user_feedback:
        payload["user_feedback"] = user_feedback
    if previous_version_id:
        payload["previous_version_id"] = previous_version_id
    return _post(f"/api/brands/{brand_id}/logo/generate/", payload)


@app.tool()
def list_logos(brand_id: str, style: str = "", status: str = "") -> str:
    """
    List all logo versions for a brand. Optionally filter by style or status.

    Args:
        brand_id: UUID of the brand.
        style: Filter by logo style (e.g. 'flat_vector').
        status: Filter by status ('draft' or 'published').
    """
    params: dict = {}
    if style:
        params["style"] = style
    if status:
        params["status"] = status
    return _get(f"/api/brands/{brand_id}/logos/", params)


@app.tool()
def publish_logo(brand_id: str, logo_id: str) -> str:
    """
    Publish a specific logo version for its style. Unpublishes any previously
    published logo of the same style.

    Args:
        brand_id: UUID of the brand.
        logo_id: UUID of the logo version to publish.
    """
    return _post(f"/api/brands/{brand_id}/logo/{logo_id}/publish/")


# ═══════════════════════════════════════════════════════════════════════════
# Website UI
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def generate_website_ui(
    brand_id: str,
    user_feedback: str = "",
    previous_version_id: str = "",
) -> str:
    """
    Generate a landing page hero section UI design image using Gemini.
    Produces a 1440px desktop mockup with: navigation bar, hero content area,
    and a visual system element — all derived from the brand analysis,
    published color palette, published typography, and primary logo.

    No publish flow — all versions are stored and browsable.

    Args:
        brand_id: UUID of the brand.
        user_feedback: Refinement notes (e.g. "darker background, more whitespace").
        previous_version_id: UUID of a previous website UI version to refine from.
    """
    payload: dict = {}
    if user_feedback:
        payload["user_feedback"] = user_feedback
    if previous_version_id:
        payload["previous_version_id"] = previous_version_id
    return _post(f"/api/brands/{brand_id}/website-ui/generate/", payload)


@app.tool()
def list_website_uis(brand_id: str) -> str:
    """
    List all website UI versions for a brand (newest first).

    Args:
        brand_id: UUID of the brand.
    """
    return _get(f"/api/brands/{brand_id}/website-uis/")


# ═══════════════════════════════════════════════════════════════════════════
# Asset Feedback (thumbs up / thumbs down)
# ═══════════════════════════════════════════════════════════════════════════

@app.tool()
def rate_asset(
    brand_id: str,
    asset_type: str,
    rating: str,
    asset_id: str = "",
) -> str:
    """
    Rate a generated brand asset as positive (thumbs up) or negative (thumbs down).
    Use this after showing an asset to the user and asking for their reaction.

    asset_type values and whether asset_id is required:
      "analysis"      — brand analysis report (no asset_id needed)
      "color_palette" — a color palette version (asset_id = palette UUID)
      "typography"    — a typography version (asset_id = typography UUID)
      "brand_name"    — a brand name version (asset_id = brand name UUID)
      "logo"          — a logo version (asset_id = logo UUID)
      "website_ui"    — a website UI version (asset_id = website UI UUID)

    Args:
        brand_id:   UUID of the brand.
        asset_type: One of the asset types listed above.
        rating:     "positive" (thumbs up / liked) or "negative" (thumbs down / disliked).
        asset_id:   UUID of the specific asset version — required for all types except "analysis".
    """
    if rating not in ("positive", "negative"):
        return '{"error": "rating must be \\"positive\\" or \\"negative\\""}'

    path_map = {
        "analysis":      f"/api/brands/{brand_id}/analysis/feedback/",
        "color_palette": f"/api/brands/{brand_id}/color-palette/{asset_id}/feedback/",
        "typography":    f"/api/brands/{brand_id}/typography/{asset_id}/feedback/",
        "brand_name":    f"/api/brands/{brand_id}/brand-name/{asset_id}/feedback/",
        "logo":          f"/api/brands/{brand_id}/logo/{asset_id}/feedback/",
        "website_ui":    f"/api/brands/{brand_id}/website-ui/{asset_id}/feedback/",
    }

    if asset_type not in path_map:
        return f'{{"error": "Unknown asset_type: {asset_type}. Must be one of: {list(path_map.keys())}"}}'

    if asset_type != "analysis" and not asset_id:
        return f'{{"error": "asset_id is required for asset_type \\"{asset_type}\\""}}'

    return _post(path_map[asset_type], {"rating": rating})


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run()
