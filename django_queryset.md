# Django QuerySet Operations Guide

A comprehensive guide to performing database queries in Django, from basic to advanced operations.

## Table of Contents

- [Basic Queries](#basic-queries)
- [Filtering Operations](#filtering-operations)
- [Aggregation and Annotation](#aggregation-and-annotation)
- [Complex Queries](#complex-queries)
- [Related Field Queries](#related-field-queries)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Basic Queries

### Retrieving All Records

```python
# Get all records from a model
customers = Customer.objects.all()

# Print the SQL query
print(customers.query)

# Check query execution time
from django.db import connection
print(connection.queries)
```

### Single Record Retrieval

```python
# Get first record
first_customer = Customer.objects.first()

# Get last record
last_customer = Customer.objects.last()

# Get by primary key
customer = Customer.objects.get(pk=1)
# or
customer = Customer.objects.get(id=1)

# Get by specific field
customer = Customer.objects.get(name='John Doe')
```

### Filtering Records

```python
# Basic filtering
active_customers = Customer.objects.filter(status='active')
premium_customers = Customer.objects.filter(subscription_type='premium')

# Multiple conditions (AND)
vip_active = Customer.objects.filter(status='active', subscription_type='vip')

# Exclude records
non_premium = Customer.objects.exclude(subscription_type='premium')
```

## Filtering Operations

### Comparison Operators

```python
# Greater than
orders = Order.objects.filter(total__gt=100)

# Less than
orders = Order.objects.filter(total__lt=100)

# Greater than or equal
orders = Order.objects.filter(total__gte=100)

# Less than or equal
orders = Order.objects.filter(total__lte=100)

# Range
orders = Order.objects.filter(total__range=(100, 200))
```

### String Operations

```python
# Case-insensitive exact match
customers = Customer.objects.filter(name__iexact='john doe')

# Contains
customers = Customer.objects.filter(name__contains='John')

# Case-insensitive contains
customers = Customer.objects.filter(name__icontains='john')

# Starts with
customers = Customer.objects.filter(name__startswith='J')

# Ends with
customers = Customer.objects.filter(name__endswith='Doe')
```

### Date Operations

```python
from django.utils import timezone
import datetime

# Get orders from today
today_orders = Order.objects.filter(created_at__date=timezone.now().date())

# Get orders from last 7 days
week_orders = Order.objects.filter(
    created_at__gte=timezone.now() - datetime.timedelta(days=7)
)

# Get orders by year
year_orders = Order.objects.filter(created_at__year=2024)

# Get orders by month
month_orders = Order.objects.filter(created_at__month=1)
```

## Aggregation and Annotation

### Basic Aggregation

```python
from django.db.models import Avg, Count, Min, Max, Sum

# Count total orders
total_orders = Order.objects.count()

# Sum of order totals
total_revenue = Order.objects.aggregate(Sum('total'))

# Multiple aggregations
stats = Order.objects.aggregate(
    total_revenue=Sum('total'),
    order_count=Count('id'),
    avg_order=Avg('total'),
    max_order=Max('total'),
    min_order=Min('total')
)
```

### Annotations

```python
from django.db.models import F, Value, CharField

# Add calculated field
customers = Customer.objects.annotate(
    full_name=Concat('first_name', Value(' '), 'last_name')
)

# Calculate order count per customer
customers = Customer.objects.annotate(
    order_count=Count('order')
)

# Calculate total spent per customer
customers = Customer.objects.annotate(
    total_spent=Sum('order__total')
)
```

## Complex Queries

### Q Objects for OR Operations

```python
from django.db.models import Q

# OR condition
customers = Customer.objects.filter(
    Q(status='active') | Q(subscription_type='premium')
)

# Complex conditions
customers = Customer.objects.filter(
    Q(status='active') & (Q(subscription_type='premium') | Q(is_vip=True))
)

# Negation
customers = Customer.objects.filter(~Q(status='inactive'))
```

### F Objects for Field Comparisons

```python
from django.db.models import F

# Compare fields
orders = Order.objects.filter(total_items__gt=F('shipped_items'))

# Arithmetic operations
orders = Order.objects.filter(
    total_amount__gt=F('base_amount') + F('tax_amount')
)
```

## Related Field Queries

### Forward Relationships (ForeignKey)

```python
# Get all orders for a customer
customer_orders = customer.order_set.all()

# Filter related records
premium_orders = Order.objects.filter(customer__subscription_type='premium')

# Nested relationships
items = OrderItem.objects.filter(
    order__customer__subscription_type='premium'
)
```

### Reverse Relationships

```python
# Get customer for an order
order = Order.objects.first()
customer = order.customer

# Prefetch related for optimization
orders = Order.objects.prefetch_related('items').all()
customers = Customer.objects.prefetch_related('order_set').all()
```

### Many-to-Many Relationships

```python
# Get all products with specific tag
products = Product.objects.filter(tags__name='electronics')

# Get all tags for a product
product_tags = product.tags.all()

# Add/Remove relationships
product.tags.add(tag1, tag2)
product.tags.remove(tag1)
```

## Performance Optimization

### Select Related

```python
# Efficient querying for foreign keys
orders = Order.objects.select_related('customer').all()

# Multiple levels
items = OrderItem.objects.select_related(
    'order__customer'
).all()
```

### Prefetch Related

```python
# Efficient querying for reverse relationships
customers = Customer.objects.prefetch_related('order_set').all()

# Multiple prefetch
orders = Order.objects.prefetch_related(
    'items',
    'items__product'
).all()
```

### Defer and Only

```python
# Defer loading of specific fields
customers = Customer.objects.defer('description', 'metadata').all()

# Only load specific fields
customers = Customer.objects.only('name', 'email').all()
```

## Best Practices

### Batch Operations

```python
# Bulk create
Customer.objects.bulk_create([
    Customer(name='John'),
    Customer(name='Jane'),
])

# Bulk update
Customer.objects.filter(status='inactive').update(status='active')
```

### Exists Checks

```python
# Check if records exist
has_orders = Order.objects.filter(customer=customer).exists()

# More efficient than count() for existence check
if Order.objects.filter(status='pending').exists():
    # Handle pending orders
```

### Query Optimization

```python
# Use values() for dictionary output
customer_data = Customer.objects.values('name', 'email')

# Use values_list() for flat lists
customer_names = Customer.objects.values_list('name', flat=True)

# Combine multiple optimizations
orders = Order.objects.select_related('customer')\
    .prefetch_related('items')\
    .filter(status='active')\
    .exclude(total=0)\
    .order_by('-created_at')
```

## Common Patterns

### Conditional Aggregation

```python
from django.db.models import Count, Case, When, IntegerField

customers = Customer.objects.annotate(
    active_orders=Count(
        Case(
            When(order__status='active', then=1),
            output_field=IntegerField(),
        )
    )
)
```

### Complex Filtering with Subqueries

```python
from django.db.models import Subquery, OuterRef

latest_orders = Order.objects.filter(
    customer=OuterRef('pk')
).order_by('-created_at')

customers = Customer.objects.annotate(
    latest_order_date=Subquery(
        latest_orders.values('created_at')[:1]
    )
)
```

## Using Raw SQL

```python
# Raw SQL queries
Customer.objects.raw('SELECT * FROM customers WHERE status = %s', ['active'])

# Custom SQL execution
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("UPDATE customers SET status = %s", ['active'])
```

## Additional Tips

1. Always use `.exists()` instead of `len()` or `.count()` for checking existence
2. Use `.iterator()` for large querysets to reduce memory usage
3. Use `.select_for_update()` for row-level locking in transactions
4. Implement proper indexing on frequently queried fields
5. Use `.bulk_create()` and `.bulk_update()` for batch operations
6. Cache complex query results when possible
7. Use `.explain()` to analyze query performance

## License

This guide is licensed under the MIT License - see the LICENSE file for details.
