---
id: "django-pattern-001"
title: "Django ORM Patterns"
category: "pattern"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - django
  - orm
  - queryset
  - n+1
  - performance
  - database
---

# Django ORM Patterns

## Problem

Django ORM code that generates N+1 queries, loads more data than needed, uses inefficient aggregations, or triggers database hits in unexpected places (like template rendering).

## Solution: select_related vs prefetch_related

These are the primary tools for avoiding N+1 queries in Django.

```python
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=200)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')

# N+1 problem: 1 query for books + N queries for each author
books = Book.objects.all()
for book in books:
    print(book.author.name)  # each access hits the database!

# select_related: JOIN for ForeignKey and OneToOne fields
# 1 query total (JOIN) instead of 1+N
books = Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)  # no additional queries

# prefetch_related: separate queries for ManyToMany and reverse ForeignKey
# 2 queries (books + tags) instead of 1+N
books = Book.objects.prefetch_related('tags').all()
for book in books:
    print([tag.name for tag in book.tags.all()])  # no additional queries

# Combined: chain when you need both
books = Book.objects.select_related('author').prefetch_related('tags')
```

## Solution: Bulk Operations

```python
# Bad: saving in a loop — N queries
for name in author_names:
    Author.objects.create(name=name)  # N separate INSERT queries

# Good: bulk_create — 1 query
authors = [Author(name=name) for name in author_names]
Author.objects.bulk_create(authors, batch_size=500)

# Good: bulk_update — update specific fields on multiple objects
for book in books:
    book.title = book.title.title()

Book.objects.bulk_update(books, fields=['title'], batch_size=500)

# Good: update() — single UPDATE query for all matching rows
Book.objects.filter(status='draft').update(status='published', updated_at=now())

# Delete: single DELETE query
Book.objects.filter(created_at__lt=cutoff_date).delete()
```

## Solution: Annotation, F() Expressions, and Q() Objects

```python
from django.db.models import Count, Avg, F, Q, Sum

# Annotate with aggregate values — single query
books = Book.objects.annotate(
    review_count=Count('reviews'),
    avg_rating=Avg('reviews__rating'),
)
for book in books:
    print(f"{book.title}: {book.review_count} reviews, avg {book.avg_rating:.1f}")

# F() expressions: reference model fields in expressions (no Python-side load needed)
# Update a counter without loading the object:
Book.objects.filter(id=book_id).update(view_count=F('view_count') + 1)

# F() in filters: compare two fields on the same model
# Find books where view_count exceeds download_count
popular_books = Book.objects.filter(view_count__gt=F('download_count'))

# Q() objects: complex OR/AND queries
from django.utils import timezone

featured_or_recent = Book.objects.filter(
    Q(is_featured=True) |
    Q(created_at__gte=timezone.now() - timedelta(days=7))
)

# Negate with ~Q()
not_archived = Book.objects.filter(~Q(status='archived'))
```

## Solution: values() and values_list()

When you only need specific fields, avoid loading full model instances.

```python
# Bad: loads full model instances when only name and email needed
users = User.objects.all()
emails = [u.email for u in users]

# Good: values_list for flat data
emails = User.objects.values_list('email', flat=True)  # QuerySet of strings

# Good: values() for dict-like results
user_dicts = User.objects.values('id', 'name', 'email')
# [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}, ...]

# Useful for feeding into serializers or reporting queries:
report_data = (
    Order.objects
    .values('status')
    .annotate(count=Count('id'), total=Sum('amount'))
    .order_by('status')
)
```

## Solution: Transactions

Wrap operations that must succeed or fail together in a transaction.

```python
from django.db import transaction

@transaction.atomic
def transfer_funds(from_account_id, to_account_id, amount):
    # Both updates are in one transaction
    Account.objects.filter(id=from_account_id).update(balance=F('balance') - amount)
    Account.objects.filter(id=to_account_id).update(balance=F('balance') + amount)
    # If either raises, the whole transaction rolls back automatically

# Savepoints for nested transactions
def complex_operation():
    with transaction.atomic():
        create_primary_record()
        try:
            with transaction.atomic():  # savepoint
                create_optional_record()  # if this fails...
        except Exception:
            pass  # ...only this is rolled back; primary_record is preserved
```

## When to Use

- `select_related`: for ForeignKey/OneToOne accessed in a loop.
- `prefetch_related`: for ManyToMany or reverse ForeignKey accessed in a loop.
- `bulk_create`/`bulk_update`: whenever creating or updating 10+ objects.
- `F()` expressions: for counter increments and field comparisons to avoid race conditions.
- `values()`/`values_list()`: when displaying data and not modifying it.

## When NOT to Use

- Do not use `select_related` for ManyToMany fields — it doesn't work and has no effect; use `prefetch_related`.
- Do not use `bulk_create` when you need `post_save` signals — they are not fired.
- Do not over-annotate a QuerySet that is then filtered down — annotate after filtering for efficiency.

## Related Patterns

- `docs/frameworks/django-orm-reference.md` — Full ORM reference
- `beh-005` — Performance Review Instructions
