---
id: "auth-pattern-002"
title: "OAuth 2.0 Patterns"
category: "pattern"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - auth
  - oauth2
  - pkce
  - security
  - tokens
---

# OAuth 2.0 Patterns

## Problem

OAuth implementations using the wrong flow for the context, storing tokens insecurely, skipping the state parameter (leaving users vulnerable to CSRF attacks), or implementing the authorization code flow without PKCE (leaving mobile/SPA apps vulnerable to authorization code interception).

## Solution: OAuth 2.0 Flows — When to Use Which

```
┌─────────────────────────────────────────────────────────────────┐
│                    Flow Selection Guide                          │
│                                                                  │
│  Has a user?                                                     │
│  ├── YES: Web app with backend?                                  │
│  │         ├── YES → Authorization Code Flow                     │
│  │         └── NO (SPA/mobile) → Authorization Code + PKCE       │
│  └── NO: Server-to-server?                                       │
│           └── YES → Client Credentials Flow                      │
└─────────────────────────────────────────────────────────────────┘
```

**Authorization Code Flow (server-side web apps):**
```
1. User clicks "Login with GitHub"
2. Browser redirects to: https://github.com/login/oauth/authorize
   ?client_id=CLIENT_ID
   &redirect_uri=https://app.com/callback
   &scope=user:email
   &state=RANDOM_CSRF_TOKEN         ← REQUIRED
   &response_type=code

3. GitHub redirects back: https://app.com/callback?code=AUTH_CODE&state=SAME_TOKEN

4. Backend exchanges code for token (server-to-server, client_secret NOT exposed):
   POST https://github.com/login/oauth/access_token
   { client_id, client_secret, code, redirect_uri }

5. Backend stores token securely, never exposes to browser
```

**Authorization Code + PKCE (SPAs, mobile apps):**
```python
import secrets, hashlib, base64

# Step 1: Generate code verifier and challenge
code_verifier = secrets.token_urlsafe(64)  # random, 43-128 chars
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode()

# Step 2: Authorization URL includes code_challenge (public, safe to expose)
auth_url = (
    f"https://auth.example.com/authorize"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
    f"&state={session_state}"
)

# Step 3: Token exchange includes code_verifier (proves you started the flow)
# POST /token
# { grant_type, code, redirect_uri, code_verifier }
# No client_secret needed — PKCE proves ownership of the flow
```

**Client Credentials (machine-to-machine):**
```python
import httpx

async def get_service_token(client_id: str, client_secret: str, token_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'read:data write:data',
        })
        response.raise_for_status()
        return response.json()['access_token']
```

## Solution: Token Storage

```javascript
// Server-side (web app with backend): store in session or database
// Client never sees the token

// SPA (PKCE flow):
// Best: HttpOnly cookie set by a BFF (Backend-for-Frontend)
// Second: in-memory variable (lost on refresh, requiring re-auth or silent refresh)
let accessToken = null;  // in-memory, never persisted to localStorage

// Mobile: use platform secure storage
// iOS: Keychain
// Android: Keystore / EncryptedSharedPreferences
```

## Solution: The State Parameter is NOT Optional

```javascript
// ALWAYS validate the state parameter to prevent CSRF attacks
// Step 1: generate state before redirect
const state = crypto.randomUUID();
sessionStorage.setItem('oauth_state', state);  // or server-side session

// Step 2: include in authorization URL
const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
authUrl.searchParams.set('state', state);
// ...

// Step 3: validate on callback — REJECT if mismatch
const urlParams = new URLSearchParams(window.location.search);
const returnedState = urlParams.get('state');
const savedState = sessionStorage.getItem('oauth_state');

if (returnedState !== savedState) {
  throw new Error('OAuth state mismatch — possible CSRF attack');
}
sessionStorage.removeItem('oauth_state');  // one-time use
```

## Solution: Common Implementation Mistakes

```python
# Mistake 1: Exposing client_secret in a SPA/mobile app
# client_secret MUST stay on the server — use PKCE instead for public clients

# Mistake 2: Not validating access tokens on your resource server
# Always verify the token is from YOUR authorization server and for YOUR audience
import jwt
payload = jwt.decode(
    token,
    public_key,
    algorithms=['RS256'],
    audience='your-api-resource-id',  # validates aud claim
    issuer='https://your-auth-server.com',  # validates iss claim
)

# Mistake 3: Not implementing token refresh
# Access tokens expire — implement silent refresh
async def ensure_valid_token(token_store):
    if token_store.is_expired():
        await token_store.refresh()  # use refresh token to get new access token
    return token_store.access_token

# Mistake 4: Putting authorization logic in the auth server
# Auth server handles AUTHENTICATION (who you are)
# Your API handles AUTHORIZATION (what you can do)
# Don't conflate the two
```

## When to Use

- Authorization Code + PKCE: any user-facing app (web SPA, mobile, desktop).
- Authorization Code (without PKCE): server-rendered web apps with a backend (and use PKCE anyway — it's free security).
- Client Credentials: microservices, background jobs, API-to-API communication.

## When NOT to Use

- **Never** use Implicit Flow (deprecated in OAuth 2.1) — tokens appear in URL fragments.
- **Never** use Resource Owner Password Credentials (ROPC) — exposes user credentials to your app.
- **Never** use client_secret in a public client (SPA, mobile).

## Related Patterns

- `auth-pattern-001` — JWT Patterns
- `beh-004` — Auth Security Instructions
