---
id: "gen-pattern-001"
title: "Clean Code Principles"
category: "pattern"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - clean-code
  - naming
  - readability
  - best-practices
---

# Clean Code Principles

## Problem

Codebases that are difficult to read, maintain, and extend. Code that requires deep familiarity to understand, that mixes concerns, uses opaque naming, or relies on implicit knowledge baked into magic numbers and deeply nested logic.

## Solution: Meaningful Naming

Names should reveal intent. A reader should understand what a variable or function does without reading its implementation.

**Python:**
```python
# Bad
def calc(d, r):
    return d * (1 - r)

# Good
def calculate_discounted_price(original_price: float, discount_rate: float) -> float:
    return original_price * (1 - discount_rate)
```

**JavaScript:**
```javascript
// Bad
const x = users.filter(u => u.s === 1);

// Good
const activeUsers = users.filter(user => user.status === 'active');
```

## Solution: Single Responsibility

Every function should do one thing. If you need "and" to describe what a function does, it probably does too much.

**Python:**
```python
# Bad: this function validates, transforms, AND saves
def process_user(raw_data: dict) -> bool:
    if not raw_data.get('email'):
        return False
    email = raw_data['email'].strip().lower()
    user = User(email=email, name=raw_data.get('name', 'Unknown'))
    db.session.add(user)
    db.session.commit()
    send_welcome_email(user)
    return True

# Good: each function does one thing
def validate_user_data(raw_data: dict) -> dict:
    if not raw_data.get('email'):
        raise ValueError("Email is required")
    return {
        'email': raw_data['email'].strip().lower(),
        'name': raw_data.get('name', 'Unknown'),
    }

def create_user(data: dict) -> User:
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user

def register_user(raw_data: dict) -> User:
    data = validate_user_data(raw_data)
    user = create_user(data)
    send_welcome_email(user)
    return user
```

## Solution: Small Functions

Functions longer than 20-30 lines are hard to test and reason about. Extract logical chunks into named helpers.

**JavaScript:**
```javascript
// Bad: 60-line monolith
function handleCheckout(cart, user, paymentInfo) {
  // validate cart...
  // validate user...
  // process payment...
  // create order...
  // send email...
  // update inventory...
}

// Good: composed from focused sub-functions
async function handleCheckout(cart, user, paymentInfo) {
  validateCart(cart);
  validateUser(user);
  const charge = await processPayment(paymentInfo, cart.total);
  const order = await createOrder(cart, user, charge);
  await Promise.all([
    sendOrderConfirmation(order, user),
    decrementInventory(cart.items),
  ]);
  return order;
}
```

## Solution: Avoid Deep Nesting

More than 3 levels of nesting makes code hard to follow. Use early returns (guard clauses) and extract helpers.

**Python:**
```python
# Bad: 4+ levels of nesting
def process(user, order):
    if user:
        if user.is_active:
            if order:
                if order.items:
                    for item in order.items:
                        if item.in_stock:
                            fulfill(item)

# Good: guard clauses flatten the logic
def process(user, order):
    if not user or not user.is_active:
        return
    if not order or not order.items:
        return

    in_stock_items = [item for item in order.items if item.in_stock]
    for item in in_stock_items:
        fulfill(item)
```

## Solution: No Magic Numbers

Named constants make intent clear and make changes safe.

**Python:**
```python
# Bad
if score > 0.75:
    label = "high"
elif score > 0.5:
    label = "medium"

# Good
HIGH_CONFIDENCE_THRESHOLD = 0.75
MEDIUM_CONFIDENCE_THRESHOLD = 0.50

if score > HIGH_CONFIDENCE_THRESHOLD:
    label = "high"
elif score > MEDIUM_CONFIDENCE_THRESHOLD:
    label = "medium"
```

**JavaScript:**
```javascript
// Bad
setTimeout(flush, 30000);

// Good
const FLUSH_INTERVAL_MS = 30_000;
setTimeout(flush, FLUSH_INTERVAL_MS);
```

## Solution: Self-Documenting Code

Code that requires a comment to explain what it does should be refactored. Comments should explain *why*, not *what*.

```python
# Bad: comment re-states what the code does
# Multiply price by 1 minus the discount rate
total = price * (1 - discount_rate)

# Good: the code explains itself; comment explains the WHY
# Early-bird pricing caps the maximum discount at 30% per policy CAP-2024
discount_rate = min(raw_discount_rate, MAX_EARLY_BIRD_DISCOUNT)
total = price * (1 - discount_rate)
```

## When to Use

- Always. These are baseline quality standards, not optional improvements.
- During code review, flag violations with [SUGGESTION] or [WARNING] per severity.

## When NOT to Use

- Do not refactor working code just to apply these principles unless you have tests confirming behavior preservation.
- Do not prioritize style purity over shipping functionality when under deadline — but do leave a TODO with a brief explanation.

## Related Patterns

- `gen-pattern-002` — Error Handling Patterns
- `gen-pattern-003` — Async Patterns
- `beh-001` — Code Review Instructions
- `beh-003` — Refactoring Instructions
