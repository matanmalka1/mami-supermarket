# Tests Directory Structure

This directory contains all backend API tests organized by domain.

## Structure

```
tests/
├── conftest.py                 # Shared fixtures (test_app, session, auth_header, etc.)
│
├── auth/                       # Authentication & Authorization
│   └── test_auth.py           # register, login, change password
│
├── profile/                    # User Profile Management
│   ├── profile_fixtures.py    # Profile-specific fixtures
│   ├── test_profile_update.py # Phone & profile updates
│   ├── test_profile_addresses_list.py    # List & create addresses
│   ├── test_profile_addresses_update.py  # Update address
│   ├── test_profile_addresses_delete.py  # Delete address
│   └── test_profile_addresses_default.py # Set default address
│
├── cart/                       # Shopping Cart
│   └── test_cart.py           # Cart CRUD operations
│
├── catalog/                    # Product Catalog
│   └── test_catalog.py        # Categories, products, search
│
├── checkout/                   # Checkout Flow
│   └── test_checkout.py       # Preview, confirm, validation
│
├── orders/                     # Order Management
│   └── test_orders.py         # List orders, view details, cancel
│
├── ops/                        # Operations (Employee workflows)
│   └── test_ops.py            # Order picking, status changes
│
├── stock_requests/             # Stock Request Management
│   └── test_stock_requests.py # Create, review, bulk operations
│
├── branches/                   # Public Branch Endpoints
│   └── test_branches.py       # List branches, delivery slots
│
├── admin/                      # Admin Management
│   ├── test_admin_catalog.py  # Category & product CRUD
│   ├── test_admin_branches.py # Branch & inventory management
│   └── test_admin_audit.py    # Audit log retrieval
│
└── infrastructure/             # Cross-cutting concerns
    ├── test_audit_payment.py  # Audit & payment integration
    ├── test_branch_inventory.py # Branch inventory validation
    ├── test_rate_limit.py     # Rate limiting
    └── test_security_routes.py # RBAC & security

```

## Running Tests

### All tests

```bash
pytest
```

### Specific domain

```bash
pytest tests/auth/
pytest tests/checkout/
pytest tests/admin/
```

### Specific file

```bash
pytest tests/auth/test_auth.py
```

### With coverage

```bash
pytest --cov=app --cov-report=html
```

## Test Coverage

- **Auth**: 3 tests (register, login, password change)
- **Profile**: 25 tests (phone, profile, addresses CRUD)
- **Cart**: 2 tests (operations, out of stock)
- **Catalog**: 2 tests (toggle, search filters)
- **Checkout**: 7 tests (oversell, payment, idempotency, fees)
- **Orders**: 1 test (ownership validation)
- **Ops**: 2 tests (employee transitions, missing items)
- **Stock Requests**: 2 tests (bulk review, audit)
- **Branches**: 5 tests (list, slots, filters)
- **Admin**: 12 tests (catalog, branches, inventory, audit)
- **Infrastructure**: 8 tests (audit, rate limiting, RBAC, inventory)

**Total: 69+ tests**
