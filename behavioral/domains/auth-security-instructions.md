---
id: "beh-004"
title: "Auth and Security Instructions"
category: "behavioral"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - security
  - auth
  - behavioral
  - secrets
  - injection
  - jwt
---

# Auth and Security Instructions

When working on auth, security, or any code that handles credentials, tokens, or user data, follow these instructions exactly.

## Always Flag (Immediately, with [CRITICAL])

- **Hardcoded secrets or API keys** — even in comments, test fixtures, or example values. Real-looking keys in comments get committed.
- **Passwords stored in plaintext** or hashed with weak algorithms (MD5, SHA1, SHA256 without salt). These are always [CRITICAL].
- **Missing input validation on auth endpoints** — login, register, password reset, token exchange. All inputs must be validated for type, format, and length before processing.
- **SQL injection vectors** — any string concatenation into SQL queries, even in utility scripts or admin-only code.
- **XSS vulnerabilities in output** — any user-controlled data rendered into HTML without proper encoding.

## Always Recommend

- **Secrets via environment variables**: `SECRET_KEY = os.environ['SECRET_KEY']` — never hardcoded, never with a fallback that would work in production.
- **bcrypt or argon2 for password hashing**: Use `bcrypt` or `argon2-cffi` in Python, `bcryptjs` in JavaScript. Never use MD5, SHA1, or plain SHA-256 for password storage.
- **Parameterized queries everywhere**: Never use string formatting or concatenation to build SQL. Always use `?` / `%s` placeholders or an ORM.
- **Output encoding**: Escape all user-controlled content before rendering in HTML. Use template auto-escaping (Django templates, React JSX do this by default — do not bypass it).

## Never

- **Never generate example code with real-looking secrets** (e.g., `api_key = "sk-1234567890abcdef"`). Use `api_key = os.environ['API_KEY']` or `api_key = "<YOUR_API_KEY>"` instead.
- **Never suggest disabling SSL verification** (`verify=False` in requests, `rejectUnauthorized: false` in Node.js) even for debugging. Suggest using a proper cert bundle or local CA instead.
- **Never recommend rolling your own crypto** (custom encryption, custom hashing, custom token generation). Always use established libraries and standards.

## On JWT Specifically

- **Always check the algorithm** is not `"none"`. When decoding, always specify the allowed algorithms explicitly as a list: `algorithms=['HS256']`, never `algorithms=None`.
- **Always verify expiry** is set on tokens you issue. Access tokens: max 15-60 minutes. Refresh tokens: max 30 days.
- **Always check audience claim** in multi-tenant apps or microservices. A token issued for `api.service-a.com` should not be accepted by `api.service-b.com`.
- **Never put sensitive data in JWT payload** — it is Base64-encoded, not encrypted. Anyone with the token can decode the payload.

## Security Review Checklist

When asked to review auth or security code, always check:

1. Are secrets loaded from environment, not hardcoded?
2. Are passwords hashed with bcrypt/argon2?
3. Are all user inputs validated?
4. Are database queries parameterized?
5. Is user-controlled output encoded before rendering?
6. Are JWT algorithms explicitly allowlisted?
7. Do JWTs have expiry set?
8. Is HTTPS enforced in production config?
9. Are session tokens unpredictable (sufficient entropy)?
10. Are rate limits in place on auth endpoints?
