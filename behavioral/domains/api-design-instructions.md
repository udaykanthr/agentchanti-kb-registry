---
id: "beh-006"
title: "API Design Instructions"
category: "behavioral"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - api-design
  - behavioral
  - rest
  - http
  - versioning
---

# API Design Instructions

When designing or reviewing APIs, follow these instructions exactly.

## Always Check

- **Consistent naming**: Resource names are nouns, not verbs. `GET /users` not `GET /getUsers`. `POST /orders` not `POST /createOrder`.
- **Proper HTTP method usage**:
  - `GET`: read-only, idempotent, cacheable
  - `POST`: create or non-idempotent action
  - `PUT`: full replacement of a resource
  - `PATCH`: partial update of a resource
  - `DELETE`: remove a resource
- **Appropriate status codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 500 Internal Server Error.
- **Pagination on list endpoints**: Any endpoint that returns a collection must have pagination. Flag unbounded list responses.
- **Versioning strategy present**: APIs that may change must have a versioning strategy (`/v1/`, `Accept-Version` header, or content negotiation).

## Always Include in API Design

- **Request/response schema**: Document the fields, types, and whether they are required or optional.
- **Error response format**: Define a consistent error body. Recommend: `{"error": "human message", "code": "machine_readable_code", "details": [...]}`.
- **Authentication requirement documented**: Each endpoint must note whether it requires authentication and what scope/role is needed.

## Never

- **Never use GET for state-changing operations.** A GET request must never modify data. Crawlers, browser prefetch, and caches all follow links — a state-changing GET causes unintended mutations.
- **Never return 200 for errors.** An error must use a 4xx or 5xx status code so clients can handle it without parsing the body. Returning `{"success": false}` with status 200 is an anti-pattern.
- **Never expose internal error details in production responses.** Stack traces, SQL errors, and internal paths must never appear in API responses. Log them server-side. Return a generic message to clients.

## REST Resource Naming

- Use **plural nouns**: `/users`, `/orders`, `/products`
- Nest **maximum 2 levels**: `/users/{id}/orders` (OK) but not `/users/{id}/orders/{id}/items/{id}/variants` (too deep — flatten it)
- Use **kebab-case** for multi-word resources: `/order-items` not `/orderItems` or `/order_items`
- Sub-actions: use a noun under the resource: `POST /users/{id}/password-reset` not `POST /resetUserPassword/{id}`

## HTTP Status Code Quick Reference

| Scenario | Code |
|---|---|
| Successful read | 200 OK |
| Created new resource | 201 Created |
| Successful with no response body | 204 No Content |
| Bad input from client | 400 Bad Request |
| Missing/invalid auth token | 401 Unauthorized |
| Valid token, insufficient permissions | 403 Forbidden |
| Resource not found | 404 Not Found |
| Conflict (e.g., duplicate unique field) | 409 Conflict |
| Validation error (schema failed) | 422 Unprocessable Entity |
| Server error | 500 Internal Server Error |
| Service temporarily unavailable | 503 Service Unavailable |

## API Review Output Format

```
## API Review: POST /users/create

[CRITICAL] Using POST /users/create — the verb "create" is redundant in REST.
→ Fix: POST /users (POST to a collection implies creation)

[WARNING] Returns 200 with {"success": false, "error": "email taken"} on conflict.
→ Fix: Return 409 Conflict with {"error": "Email already registered", "code": "email_conflict"}

[WARNING] No pagination on GET /users — will return all users.
→ Fix: Add ?page=1&per_page=50 query parameters, return X-Total-Count and Link headers.

[SUGGESTION] Document auth requirement: which endpoints require a JWT?
→ Add security scheme to OpenAPI spec or add auth notes to each endpoint.
```
