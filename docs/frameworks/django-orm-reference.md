---
id: "doc-007"
title: "Django ORM Reference Cheatsheet"
category: "doc"
language: "python"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - django
  - orm
  - queryset
  - database
  - cheatsheet
---

# Django ORM Reference Cheatsheet

## QuerySet API

```python
from myapp.models import Article, Author

# Retrieval
Article.objects.all()                             # all records
Article.objects.filter(status='published')        # WHERE status='published'
Article.objects.exclude(status='draft')           # WHERE NOT status='draft'
Article.objects.get(id=1)                         # exactly one — raises if 0 or >1
Article.objects.first()                           # first record or None
Article.objects.last()                            # last record or None
Article.objects.count()                           # SELECT COUNT(*)
Article.objects.exists()                          # efficient "any?" check

# Ordering
Article.objects.order_by('created_at')            # ASC
Article.objects.order_by('-created_at')           # DESC
Article.objects.order_by('author__name', '-id')   # multi-field

# Slicing (uses LIMIT/OFFSET)
Article.objects.all()[:10]      # LIMIT 10
Article.objects.all()[10:20]    # LIMIT 10 OFFSET 10
```

## Field Lookups

```python
# Exact matches
.filter(status='published')          # = 'published'
.filter(status__exact='published')   # same

# Comparison
.filter(views__gt=100)               # > 100
.filter(views__gte=100)              # >= 100
.filter(views__lt=100)               # < 100
.filter(views__lte=100)              # <= 100

# Null checks
.filter(deleted_at__isnull=True)     # IS NULL
.filter(deleted_at__isnull=False)    # IS NOT NULL

# String matching
.filter(title__contains='Python')    # LIKE '%Python%' (case-sensitive)
.filter(title__icontains='python')   # ILIKE '%python%' (case-insensitive)
.filter(title__startswith='How')     # LIKE 'How%'
.filter(title__endswith='Guide')     # LIKE '%Guide'

# In list
.filter(status__in=['published', 'featured'])

# Date ranges
from datetime import datetime, timedelta
.filter(created_at__date=date.today())
.filter(created_at__year=2026)
.filter(created_at__range=(start_date, end_date))

# Related fields (double underscore traversal)
.filter(author__name='Alice')
.filter(author__profile__city='London')
```

## Aggregation

```python
from django.db.models import Count, Sum, Avg, Max, Min, StdDev

# Aggregate over entire queryset
stats = Article.objects.aggregate(
    total=Count('id'),
    avg_views=Avg('views'),
    max_views=Max('views'),
)
# Returns a dict: {'total': 100, 'avg_views': 234.5, 'max_views': 9820}

# Annotate: per-object aggregate
articles = Article.objects.annotate(
    comment_count=Count('comments'),
    avg_rating=Avg('comments__rating'),
).filter(comment_count__gt=5).order_by('-avg_rating')

for article in articles:
    print(f"{article.title}: {article.comment_count} comments")
```

## values() and values_list()

```python
# values(): dict-like rows
Article.objects.filter(status='published').values('id', 'title', 'author__name')
# [{'id': 1, 'title': 'Hello', 'author__name': 'Alice'}, ...]

# values_list(): tuple rows
Article.objects.values_list('id', 'title')
# [(1, 'Hello'), (2, 'World'), ...]

# flat=True: flat list (single field only)
ids = Article.objects.values_list('id', flat=True)
# [1, 2, 3, ...]

# Combined with aggregation
from django.db.models import Count
Article.objects.values('status').annotate(count=Count('id'))
# [{'status': 'published', 'count': 85}, {'status': 'draft', 'count': 15}]
```

## bulk_create and bulk_update

```python
# bulk_create: one INSERT ... VALUES (...), (...), ...
articles = [
    Article(title=t, status='draft', author=author)
    for t in titles
]
created = Article.objects.bulk_create(articles, batch_size=500)
# Note: post_save signals are NOT fired

# bulk_update: one UPDATE ... CASE ...
for article in articles:
    article.views += 1
Article.objects.bulk_update(articles, fields=['views'], batch_size=500)

# update(): single SQL UPDATE — fastest, but no signals/save()
Article.objects.filter(status='draft', created_at__lt=cutoff).update(
    status='archived',
    updated_at=now(),
)
```

## Transactions

```python
from django.db import transaction

# Entire function is one atomic transaction
@transaction.atomic
def create_order_with_items(order_data, items_data):
    order = Order.objects.create(**order_data)
    OrderItem.objects.bulk_create([
        OrderItem(order=order, **item) for item in items_data
    ])
    return order

# Context manager for partial atomicity
def complex_operation():
    with transaction.atomic():
        do_step1()
        try:
            with transaction.atomic():  # savepoint
                do_risky_step2()
        except SomeError:
            pass  # savepoint rolled back, step1 preserved
        do_step3()

# Select for update (row-level lock — use in transactions)
with transaction.atomic():
    account = Account.objects.select_for_update().get(id=account_id)
    account.balance -= amount
    account.save()
```

## Raw SQL When Needed

```python
# Raw queryset (returns model instances)
articles = Article.objects.raw(
    'SELECT * FROM articles WHERE SIMILARITY(title, %s) > 0.3',
    [search_term]
)

# Execute raw SQL (no model mapping)
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        'UPDATE articles SET view_count = view_count + 1 WHERE id = %s',
        [article_id]
    )
    # cursor.fetchall(), cursor.fetchone() for SELECT
    cursor.execute('SELECT id, title FROM articles LIMIT 10')
    rows = cursor.fetchall()

# Always use parameterized queries — never string format for values
# WRONG:  f"WHERE id = {user_id}"  — SQL injection risk
# RIGHT:  "WHERE id = %s", [user_id]  — parameterized
```

## Common Patterns

```python
# get_or_create: atomic — won't duplicate
user, created = User.objects.get_or_create(
    email=email,
    defaults={'name': name, 'role': 'user'}
)

# update_or_create
profile, created = UserProfile.objects.update_or_create(
    user=user,
    defaults={'bio': bio, 'avatar_url': avatar_url}
)

# Only update specific fields to avoid race conditions
User.objects.filter(id=user_id).update(last_seen=now())

# Defer: exclude large fields from initial load
Article.objects.defer('body', 'metadata').all()

# Only: load only specified fields
Article.objects.only('id', 'title', 'status').all()

# select_related: JOIN for FK/O2O
Article.objects.select_related('author', 'author__profile').all()

# prefetch_related: separate query for M2M/reverse FK
Article.objects.prefetch_related('tags', 'comments').all()
```
