---
id: "auth-pattern-001"
title: "JWT Authentication Patterns"
category: "pattern"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - auth
  - jwt
  - security
  - tokens
  - refresh
---

# JWT Authentication Patterns

## Problem

JWT implementations that use weak signing algorithms, store tokens in insecure locations, never expire, or are vulnerable to algorithm confusion attacks, token replay, or missing audience/issuer validation.

## Solution: JWT Structure

A JWT has three parts: Header.Payload.Signature, each Base64url-encoded.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxNzAwMDAzNjAwfQ.signature
  └── Header                           └── Payload                                                                        └── Signature
  { alg: "HS256", typ: "JWT" }         { sub: "user-123", iat: 1700000000, exp: 1700003600 }
```

Key claims:
- `sub`: Subject (user ID)
- `iat`: Issued At (Unix timestamp)
- `exp`: Expiry (Unix timestamp) — **always set this**
- `iss`: Issuer — validate this to prevent cross-service token use
- `aud`: Audience — validate this in multi-tenant apps

## Solution: HS256 vs RS256

```python
import jwt  # PyJWT library

# HS256: symmetric — same secret for signing and verifying
# Use when: single service signs and verifies its own tokens
SECRET = os.environ['JWT_SECRET']  # min 256 bits (32 chars)
token = jwt.encode({'sub': 'user-123', 'exp': datetime.utcnow() + timedelta(hours=1)},
                   SECRET, algorithm='HS256')
payload = jwt.decode(token, SECRET, algorithms=['HS256'])  # note: list, not string!

# RS256: asymmetric — private key signs, public key verifies
# Use when: multiple services need to verify tokens (share public key, not secret)
# Or when you need to share tokens with third-party services
import jwt
from pathlib import Path

PRIVATE_KEY = Path('private.pem').read_text()
PUBLIC_KEY = Path('public.pem').read_text()

token = jwt.encode({'sub': 'user-123', 'exp': ...}, PRIVATE_KEY, algorithm='RS256')
payload = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])
```

## Solution: Token Expiry and Refresh Strategy

```python
from datetime import datetime, timedelta
import jwt

ACCESS_TOKEN_EXPIRY = timedelta(minutes=15)   # short-lived: 15 min
REFRESH_TOKEN_EXPIRY = timedelta(days=30)     # long-lived: 30 days

def create_tokens(user_id: str) -> dict:
    now = datetime.utcnow()
    access_token = jwt.encode({
        'sub': user_id,
        'type': 'access',
        'iat': now,
        'exp': now + ACCESS_TOKEN_EXPIRY,
    }, SECRET, algorithm='HS256')

    refresh_token = jwt.encode({
        'sub': user_id,
        'type': 'refresh',
        'iat': now,
        'exp': now + REFRESH_TOKEN_EXPIRY,
    }, SECRET, algorithm='HS256')

    return {'access_token': access_token, 'refresh_token': refresh_token}

def refresh_access_token(refresh_token: str) -> str:
    payload = jwt.decode(refresh_token, SECRET, algorithms=['HS256'])
    if payload.get('type') != 'refresh':
        raise ValueError("Not a refresh token")
    return create_tokens(payload['sub'])['access_token']
```

## Solution: Storing Tokens Safely

```javascript
// Bad: localStorage — vulnerable to XSS
localStorage.setItem('token', accessToken);

// Bad: sessionStorage — also XSS vulnerable
sessionStorage.setItem('token', accessToken);

// Good: HttpOnly cookies — not accessible to JavaScript (XSS safe)
// Server sets the cookie:
res.cookie('access_token', token, {
  httpOnly: true,   // JavaScript cannot read this cookie
  secure: true,     // HTTPS only
  sameSite: 'strict',  // CSRF protection
  maxAge: 15 * 60 * 1000,  // 15 minutes in ms
});

// For SPAs that cannot use cookies (e.g., mobile app with CORS):
// Store in memory (in-memory variable) — lost on page refresh
// Use a refresh token rotation strategy to re-acquire on load
```

## Solution: Common JWT Vulnerabilities and Fixes

```python
# Vulnerability 1: Algorithm confusion ("alg: none")
# Never accept "none" as a valid algorithm
payload = jwt.decode(token, SECRET, algorithms=['HS256'])  # explicit algorithm list
# NOT:  jwt.decode(token, SECRET, algorithms=None)  # allows any algorithm

# Vulnerability 2: Not validating expiry
# jwt.decode() validates exp automatically (PyJWT)
# If you need to allow expired tokens (for grace periods):
payload = jwt.decode(token, SECRET, algorithms=['HS256'],
                     options={'verify_exp': False})  # only for specific use cases

# Vulnerability 3: Not validating issuer/audience
payload = jwt.decode(token, SECRET,
                     algorithms=['HS256'],
                     issuer='https://auth.example.com',  # validates iss claim
                     audience='api.example.com')          # validates aud claim

# Vulnerability 4: Weak secret (brute-forceable)
# Use at least 256 bits (32 bytes) of random entropy:
import secrets
SECRET = secrets.token_hex(32)  # 64 hex chars = 256 bits

# Vulnerability 5: Not rotating refresh tokens
# On each refresh: issue new refresh token AND invalidate the old one
# Store refresh token IDs in a database to allow server-side revocation
```

## When to Use

- JWT: for stateless authentication in APIs where you don't want to look up sessions in a DB.
- HS256: single-service tokens, internal APIs.
- RS256: multi-service architectures, public APIs, tokens shared with third parties.

## When NOT to Use

- Do not use JWT for sessions if you need instant revocation (JWT can't be "logged out" without a blocklist).
- Do not put sensitive data in JWT payload — it is Base64-encoded, not encrypted. Anyone can decode it.
- Do not use long expiry (>1 hour) for access tokens — use refresh tokens instead.

## Related Patterns

- `auth-pattern-002` — OAuth Patterns
- `beh-004` — Auth Security Instructions
