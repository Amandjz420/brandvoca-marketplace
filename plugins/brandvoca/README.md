# BrandVoca Plugin

AI-powered brand identity tools for Claude and Codex. Connects to your BrandVoca backend and lets you generate color palettes, typography systems, logo images, and landing page UI designs directly from a conversation.

## Runtime Layout

- Claude manifest: `.claude-plugin/plugin.json`
- Codex manifest: `.codex-plugin/plugin.json`
- Claude MCP config: `.mcp.json`
- Codex MCP config: `.mcp.codex.json`

The Claude and Codex manifests coexist, so you can support both runtimes from the same plugin folder and the same shared skills/MCP implementation.

## Components

| Component | Type | Purpose |
|-----------|------|---------|
| `brand-workflow` | Skill | End-to-end brand creation pipeline guide |
| `brand-assets` | Skill | Generate/refine specific brand assets |
| `account-management` | Skill | Credits, subscriptions, pricing, transaction history |
| `brandvoca` | MCP Server | REST API wrapper — all BrandVoca endpoints as tools |

## Setup

### 1. Install Python dependencies

The MCP server requires Python 3.10+ and two packages:

```bash
pip install mcp httpx
# or
pip install -r /path/to/plugin/mcp-server/requirements.txt
```

### 2. Set environment variables

Add these to your shell profile (`~/.zshrc`, `~/.bashrc`) or your system environment:

```bash
# Required: your BrandVoca API bearer token
export BRANDVOCA_API_KEY="your_bearer_token_here"

# Optional: override the API URL (defaults to https://brandvoca-backend-production.up.railway.app)
export BRANDVOCA_API_URL="https://brandvoca-backend-production.up.railway.app"
```

Claude and Codex both use the same `BRANDVOCA_API_KEY` value for authentication.

### 3. How to get your API key

Your Django backend uses `Authorization: Bearer <token>`. There are two common ways to issue tokens:

**Option A — DRF Token Auth** (if using `rest_framework.authtoken`):
```python
# In Django shell
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
user = User.objects.get(username="your_username")
token, _ = Token.objects.get_or_create(user=user)
print(token.key)  # use this as BRANDVOCA_API_KEY
```

**Option B — djangorestframework-api-key** (if using the `djangorestframework-api-key` package):
- Go to `/admin/rest_framework_api_key/apikey/` in your Django admin
- Click "Add API Key" → copy the generated key (shown only once)
- Use it as `BRANDVOCA_API_KEY`

**Option C — simplejwt** (if using JWT):
```bash
curl -X POST https://brandvoca-backend-production.up.railway.app/api/token/ \
  -d '{"username": "you", "password": "yourpass"}' \
  -H "Content-Type: application/json"
# Use the "access" token from the response as BRANDVOCA_API_KEY
```

> Note: JWT access tokens expire (typically after 5–60 minutes). For a long-lived plugin credential, prefer DRF Token Auth or an API key package.

## Available Tools (via MCP)

### Auth (8 tools)
| Tool | Description |
|------|-------------|
| `register` | Create a new account with username, email, password |
| `login` | Log in with username + password, stores token for session |
| `login_with_google` | Sign in/up with Google email (trusted mode) |
| `login_with_apple` | Sign in/up with Apple email (trusted mode) |
| `logout` | Revoke refresh token and clear session |
| `refresh_token` | Exchange refresh token for a new access token |
| `get_my_profile` | Get current user's profile, credits, and subscription |
| `update_profile` | Update user's email, first name, or last name |

### Subscription (2 tools)
| Tool | Description |
|------|-------------|
| `get_subscription_plans` | List all plans — Free, Pro, Max (public, no auth) |
| `get_my_subscription` | Current user's plan, status, billing period, balance |

### Credits & Payments (7 tools)
| Tool | Description |
|------|-------------|
| `get_credit_balance` | Quick credit balance check |
| `get_credit_transactions` | Paginated transaction history with filters |
| `get_model_pricing` | Credit cost per action (estimate before generating) |
| `get_credit_packs` | List purchasable one-time credit bundles (public) |
| `create_payment_order` | Create Razorpay order for subscription or credit top-up |
| `verify_payment` | Verify Razorpay payment and fulfill transaction |
| `get_payment_history` | Full payment history (subscriptions + top-ups) |

### Brand (4 tools)
| Tool | Description |
|------|-------------|
| `brand_intake` | Create a new brand from text + files; Gemini auto-fills questionnaire |
| `list_brands` | List all brands with optional search/status filters |
| `get_brand` | Full brand details (questionnaire, analysis, all published assets) |
| `delete_brand` | Permanently delete a brand and all related data |

### Questionnaire & Analysis (3 tools)
| Tool | Description |
|------|-------------|
| `get_questionnaire` | View the 30-field brand questionnaire |
| `update_questionnaire` | Update/submit questionnaire fields (set submit=True to finalize) |
| `generate_brand_analysis` | Generate 7-section analysis from completed questionnaire |

### Color Palette (4 tools)
| Tool | Description |
|------|-------------|
| `generate_color_palette` | Generate/refine a color system using Gemini |
| `get_color_palette` | Get a specific palette version by ID |
| `list_color_palettes` | List all palette versions |
| `publish_color_palette` | Publish a palette version |

### Typography (4 tools)
| Tool | Description |
|------|-------------|
| `generate_typography` | Generate/refine a font-pairing system using Gemini |
| `get_typography` | Get a specific typography version by ID |
| `list_typographies` | List all typography versions |
| `publish_typography` | Publish a typography version |

### Brand Name (4 tools)
| Tool | Description |
|------|-------------|
| `generate_brand_names` | Generate AI name suggestions using Grok (5 categories) |
| `get_brand_name` | Get a specific brand name version by ID |
| `list_brand_names` | List all name versions |
| `publish_brand_name` | Publish a name (propagates across all brand assets) |

### Logo (6 tools)
| Tool | Description |
|------|-------------|
| `generate_logo` | Generate a logo image in one of 6 styles using Gemini |
| `get_logo` | Get a specific logo version by ID |
| `list_logos` | List all logo versions (filter by style/status) |
| `publish_logo` | Publish a logo version |
| `upload_primary_logo` | Upload/replace the primary logo reference image |
| `delete_primary_logo` | Remove the primary logo reference image |

### Website UI (3 tools)
| Tool | Description |
|------|-------------|
| `generate_website_ui` | Generate a landing page hero section UI image |
| `get_website_ui` | Get a specific website UI version by ID |
| `list_website_uis` | List all website UI versions |

### Feedback (1 tool)
| Tool | Description |
|------|-------------|
| `rate_asset` | Rate any asset as positive/negative (thumbs up/down) |

## Usage

### Full brand setup
> "Set up a new brand for me" or "Walk me through creating a brand identity"

Claude will guide you step-by-step through the entire pipeline.

### Quick asset generation
> "Generate a flat vector logo for brand [ID]"
> "Give me a new color palette for my brand"
> "Generate website UI for [brand name]"

### Check brand status
> "What step is my brand on?"
> "Show me what's been generated for [brand ID]"

## Generation Times

Gemini image generation (logos, website UI) can take 20–60 seconds per call. Claude will let you know to wait.

## Troubleshooting

**"BRANDVOCA_API_KEY is not set"** — make sure you've exported the env var and restarted your terminal/app.

**401 Unauthorized** — your token may be expired (if using JWT) or incorrect. Re-generate it.

**500 errors from Gemini** — Gemini's image generation model occasionally returns server errors. Just retry — it's a transient issue on Google's side.
