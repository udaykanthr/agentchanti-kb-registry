---
id: "async-pattern-001"
title: "Task Queue Patterns"
category: "pattern"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - async
  - queue
  - idempotency
  - retry
  - dead-letter-queue
  - celery
  - rabbitmq
---

# Task Queue Patterns

## Problem

Task queues that lose messages, retry non-idempotent tasks causing duplicate side effects, lack dead letter queues causing poison messages to block all processing, or fail silently with no observability.

## Solution: Task Queue Fundamentals

A task queue decouples work producers from workers. Common uses: sending emails, processing uploads, generating reports, sending webhooks.

```python
# Celery example (Python)
from celery import Celery
import os

app = Celery('tasks', broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # seconds between retries
    acks_late=True,           # only ack after task completes (at-least-once delivery)
)
def send_welcome_email(self, user_id: int, email: str):
    try:
        email_client.send(
            to=email,
            template='welcome',
            user_id=user_id,
        )
    except EmailProviderError as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

## Solution: Idempotency

Tasks may run more than once (retries, at-least-once delivery). Design tasks so that running them multiple times has the same effect as running once.

```python
from django.db import transaction

@app.task(bind=True, max_retries=3)
def process_payment(self, payment_id: str, amount_cents: int):
    """
    Idempotent: uses payment_id as idempotency key.
    Safe to retry — won't charge twice.
    """
    with transaction.atomic():
        # Check if already processed
        if Payment.objects.filter(id=payment_id, status='completed').exists():
            logger.info("Payment %s already processed, skipping", payment_id)
            return  # idempotent exit

        payment = Payment.objects.select_for_update().get(id=payment_id)
        if payment.status != 'pending':
            return  # only process pending payments

        # Call external payment provider with idempotency key
        charge = stripe.Charge.create(
            amount=amount_cents,
            currency='usd',
            idempotency_key=f"payment-{payment_id}",  # Stripe won't charge twice
        )

        payment.stripe_charge_id = charge.id
        payment.status = 'completed'
        payment.save()
```

## Solution: Dead Letter Queues

Messages that fail repeatedly should be moved to a Dead Letter Queue (DLQ) instead of retrying forever. The DLQ enables inspection and manual reprocessing.

```python
# Celery: configure dead letter queue
from kombu import Exchange, Queue

CELERY_TASK_QUEUES = [
    Queue('default',
          Exchange('default'),
          routing_key='default',
          queue_arguments={
              'x-dead-letter-exchange': 'dead_letter',
              'x-dead-letter-routing-key': 'dead_letter',
          }),
    Queue('dead_letter',
          Exchange('dead_letter'),
          routing_key='dead_letter'),
]

@app.task(
    bind=True,
    max_retries=5,
    acks_late=True,
    reject_on_worker_lost=True,  # requeue if worker dies during execution
)
def process_order(self, order_id: int):
    try:
        order_service.process(order_id)
    except RecoverableError as e:
        raise self.retry(exc=e)
    except PermanentError as e:
        # Don't retry — let the message go to DLQ
        logger.error("Permanent failure for order %s: %s", order_id, e)
        raise  # will go to DLQ after max_retries
```

## Solution: Retry Strategies

```python
# Exponential backoff: delay doubles each retry
@app.task(bind=True, max_retries=5)
def exponential_retry_task(self, data):
    try:
        call_external_api(data)
    except TransientError as e:
        # Retry with exponential backoff: 60s, 120s, 240s, 480s, 960s
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

# Jitter: add randomness to prevent retry thundering herd
import random
base_delay = 60 * (2 ** self.request.retries)
jitter = random.uniform(0, 0.3 * base_delay)
raise self.retry(exc=e, countdown=base_delay + jitter)
```

## Solution: Poison Message Handling

A poison message is one that consistently causes processing errors. Without protection, it can halt an entire queue.

```python
@app.task(
    bind=True,
    max_retries=3,
    acks_late=True,
)
def process_event(self, event_id: str, payload: dict):
    try:
        # Check if this message is known to be poisonous
        if PoisonMessage.objects.filter(event_id=event_id).exists():
            logger.warning("Skipping known poison message: %s", event_id)
            return

        process(payload)

    except Exception as e:
        retry_count = self.request.retries
        if retry_count >= self.max_retries - 1:
            # This message is going to DLQ — record it
            PoisonMessage.objects.get_or_create(
                event_id=event_id,
                defaults={'error': str(e), 'payload': payload}
            )
            raise  # go to DLQ
        raise self.retry(exc=e, countdown=30 * (2 ** retry_count))
```

## Solution: At-Least-Once vs Exactly-Once Delivery

```
At-Least-Once (most common):
  - Message acknowledged AFTER successful processing
  - Risk: duplicate processing on retry
  - Mitigation: idempotent task design

At-Most-Once:
  - Message acknowledged BEFORE processing
  - Risk: message lost if worker crashes during processing
  - Use for: non-critical, fast operations where duplicate is worse than loss

Exactly-Once (very rare in distributed systems):
  - Requires distributed transactions or transactional outbox pattern
  - High overhead — only use when business absolutely requires no duplicates
```

**Transactional Outbox Pattern:**
```python
# Write to outbox table in the same transaction as the business operation
with transaction.atomic():
    order = Order.objects.create(...)
    OutboxEvent.objects.create(
        event_type='order.created',
        payload={'order_id': order.id},
    )

# Separate process reads outbox and publishes to queue
@app.task
def publish_outbox_events():
    events = OutboxEvent.objects.filter(published=False).select_for_update(skip_locked=True)
    for event in events:
        queue.publish(event.event_type, event.payload)
        event.published = True
        event.save()
```

## When to Use

- Task queues: for any operation that is slow (>200ms), uses external services, or can be retried.
- Idempotency keys: always, on tasks that have side effects.
- DLQ: always — it's your safety net for debugging production issues.
- Exponential backoff: for transient errors from external services (rate limits, timeouts).

## When NOT to Use

- Do not use task queues for operations that must complete before the HTTP response returns.
- Do not retry on validation errors or auth failures — they will never succeed.
- Do not use exactly-once delivery without understanding its complexity and overhead.

## Related Patterns

- `gen-pattern-002` — Error Handling Patterns
- `gen-pattern-003` — Async Patterns
