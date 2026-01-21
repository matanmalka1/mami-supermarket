# Mami Supermarket - Backend API Routes

## Overview

This document lists all available API endpoints in the Mami Supermarket backend.

**Base URL**: `/api/v1`

**Authentication**: Most endpoints require JWT authentication via `Authorization: Bearer <token>` header.

**Response Format**: Responses use different envelopes based on type:

**For lists (with pagination):**

```json
{
  "data": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

**For single items:**

```json
{
  "data": { ... }
}
```

**For actions (delete/toggle):**

```json
{
  "data": { "success": true }
}
```

**Error Format**:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

**Field Naming**: All request/response bodies use **snake_case** for field names (e.g., `cart_id`, `delivery_slot_id`, `is_active`). Frontend must convert from camelCase if needed.

---

## Authentication (`/api/v1/auth`)

### `GET /api/v1/auth/me`

Get current authenticated user details.

- **Auth**: Required (JWT)
- **Response**: User object with id, email, full_name, role

### `POST /api/v1/auth/register`

Register a new customer account.

- **Auth**: None
- **Body**: `{ email, password, full_name, phone }`
- **Response**: User object + JWT tokens (201)

### `POST /api/v1/auth/login`

Login with email and password.

- **Auth**: None
- **Rate Limit**: 5 requests per minute
- **Body**: `{ email, password }`
- **Response**: User object + JWT tokens
- **Audit**: LOGIN_SUCCESS / LOGIN_FAILURE

### `POST /api/v1/auth/change-password`

Change password for authenticated user.

- **Auth**: Required (JWT)
- **Body**: `{ current_password, new_password }`
- **Response**: Success message

---

## Profile & User Management (`/api/v1/me`)

### `PATCH /api/v1/me`

Update user profile information.

- **Auth**: Required (JWT)
- **Body**: `{ full_name, phone }` (fields optional)
- **Response**: Updated user object
- **Note**: Both fields are optional; send only what needs updating

### `GET /api/v1/me/addresses`

List user's saved delivery addresses.

- **Auth**: Required (JWT)
- **Response**: Array of address objects

### `POST /api/v1/me/addresses`

Add a new delivery address.

- **Auth**: Required (JWT)
- **Body**: `{ street, city, postal_code, country, is_default }`
- **Response**: Created address object (201)
- **Note**: Current model includes basic fields. Consider extending with: `apartment`, `floor`, `entrance`, `instructions`, `label` (Home/Work) for production use

### `PUT /api/v1/me/addresses/{id}`

Update an existing delivery address.

- **Auth**: Required (JWT)
- **Path Params**: `id` (UUID)
- **Body**: `{ street, city, postal_code, country }` (fields optional)
- **Ownership**: Returns 404 if address doesn't belong to user
- **Response**: Updated address object

### `DELETE /api/v1/me/addresses/{id}`

Delete a delivery address.

- **Auth**: Required (JWT)
- **Path Params**: `id` (UUID)
- **Ownership**: Returns 404 if address doesn't belong to user
- **Response**: Success message

### `PATCH /api/v1/me/addresses/{id}/default`

Set an address as the default delivery address.

- **Auth**: Required (JWT)
- **Path Params**: `id` (UUID)
- **Ownership**: Returns 404 if address doesn't belong to user
- **Response**: Updated address object

---

## Catalog (Public) (`/api/v1/catalog`)

### `GET /api/v1/catalog/categories`

List all active categories.

- **Auth**: None
- **Query Params**:
  - `limit` (default: 50, max: 200)
  - `offset` (default: 0)
- **Response**: Array of categories with pagination metadata

### `GET /api/v1/catalog/categories/{category_id}/products`

Get products in a specific category.

- **Auth**: None
- **Path Params**: `category_id` (UUID)
- **Query Params**:
  - `branchId` (UUID, optional) - show inventory for specific branch
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of products with pagination

### `GET /api/v1/catalog/products/{product_id}`

Get details for a specific product.

- **Auth**: None
- **Path Params**: `product_id` (UUID)
- **Query Params**:
  - `branchId` (UUID, optional) - include branch-specific inventory
- **Response**: Product object

### `GET /api/v1/catalog/products/search`

Search products by query, category, stock status.

- **Auth**: None
- **Query Params**:
  - `q` (string) - search query
  - `categoryId` (UUID, optional)
  - `branchId` (UUID, optional)
  - `inStock` (boolean, optional) - filter by availability
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of products with pagination

### `GET /api/v1/catalog/products/autocomplete`

Get autocomplete suggestions for product search.

- **Auth**: None
- **Query Params**:
  - `q` (string) - search query
  - `limit` (default: 10)
- **Response**: Array of product suggestions

---

## Branches (Public) (`/api/v1`)

### `GET /api/v1/branches`

List all active branches.

- **Auth**: None
- **Query Params**:
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of branches with pagination

### `GET /api/v1/delivery-slots`

Get available delivery time slots.

- **Auth**: None
- **Query Params**:
  - `dayOfWeek` (int, 0-6, optional) - filter by day
  - `branchId` (UUID, optional) - filter by branch
- **Response**: Array of delivery slots

---

## Cart (Customer Only) (`/api/v1/cart`)

### `GET /api/v1/cart`

Get current user's cart.

- **Auth**: Required (Customer)
- **Response**: Cart object with items

### `POST /api/v1/cart/items`

Add item to cart.

- **Auth**: Required (Customer)
- **Body**: `{ product_id, quantity }`
- **Response**: Updated cart object (201)

### `PUT /api/v1/cart/items/{item_id}`

Update item quantity in cart.

- **Auth**: Required (Customer)
- **Path Params**: `item_id` (UUID)
- **Body**: `{ product_id, quantity }`
- **Response**: Updated cart object

### `DELETE /api/v1/cart/items/{item_id}`

Remove item from cart.

- **Auth**: Required (Customer)
- **Path Params**: `item_id` (UUID)
- **Response**: Updated cart object

### `DELETE /api/v1/cart`

Clear entire cart.

- **Auth**: Required (Customer)
- **Response**: Empty cart object

---

## Checkout (`/api/v1/checkout`)

### `POST /api/v1/checkout/preview`

Preview order totals and fees before confirmation.

- **Auth**: Required (JWT)
- **Body**: `{ cart_id, branch_id, delivery_slot_id, delivery_address, payment_method }`
- **Response**: Order preview with totals, fees, delivery info

### `POST /api/v1/checkout/confirm`

Confirm and create order with payment.

- **Auth**: Required (JWT)
- **Headers**:
  - **`Idempotency-Key`** (required): Unique string to prevent duplicate orders
- **Body**: `{ cart_id, branch_id, delivery_slot_id, delivery_address, payment_method, payment_token }`
- **Idempotency Behavior**:
  - First request with a key: Creates new order (201)
  - Repeated request with same key + same payload: Returns cached order (200)
  - Same key + different payload: Returns 409 `IDEMPOTENCY_KEY_REUSE_MISMATCH`
  - Same key while processing: Returns 409 `IDEMPOTENCY_IN_PROGRESS`
- **Process**:
  1. Validate `Idempotency-Key` header (400 if missing)
  2. Check/create idempotency record with IN_PROGRESS status
  3. Lock inventory rows (FOR UPDATE)
  4. Verify stock availability
  5. Charge payment
  6. Create order + snapshots
  7. Decrement inventory
  8. Write audit log
  9. Mark idempotency as SUCCEEDED
  10. Commit transaction
- **Response**: Order object with order_number (201)
- **Errors**:
  - `MISSING_IDEMPOTENCY_KEY` (400) - Header not provided
  - `INSUFFICIENT_STOCK` (409) - Not enough inventory
  - `IDEMPOTENCY_KEY_REUSE_MISMATCH` (409) - Same key, different payload
  - `IDEMPOTENCY_IN_PROGRESS` (409) - Request already processing
  - `PAYMENT_FAILED` (402) - Payment charge failed

---

## Orders (Customer) (`/api/v1/orders`)

### `GET /api/v1/orders`

List current user's orders.

- **Auth**: Required (Customer)
- **Query Params**:
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of orders with pagination

### `GET /api/v1/orders/{order_id}`

Get details for a specific order.

- **Auth**: Required (Customer)
- **Path Params**: `order_id` (UUID)
- **Ownership**: Returns 404 if order doesn't belong to user
- **Response**: Order object with items

### `POST /api/v1/orders/{order_id}/cancel`

Cancel an order (only if status is CREATED).

- **Auth**: Required (Customer)
- **Path Params**: `order_id` (UUID)
- **Ownership**: Returns 404 if order doesn't belong to user
- **Response**: Updated order object

---

## Operations (Employee/Manager/Admin) (`/api/v1/ops`)

### `GET /api/v1/ops/orders`

List orders for picking/fulfillment (sorted by urgency).

- **Auth**: Required (Employee, Manager, Admin)
- **Query Params**:
  - `status` (OrderStatus enum, optional)
  - `dateFrom` (ISO date, optional)
  - `dateTo` (ISO date, optional)
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of orders with pagination

### `GET /api/v1/ops/orders/{order_id}`

Get order details for operations.

- **Auth**: Required (Employee, Manager, Admin)
- **Path Params**: `order_id` (UUID)
- **Response**: Order object with full details

### `PATCH /api/v1/ops/orders/{order_id}/items/{item_id}/picked-status`

Update picked status for an order item.

- **Auth**: Required (Employee, Manager, Admin)
- **Path Params**:
  - `order_id` (UUID)
  - `item_id` (UUID)
- **Body**: `{ picked_status }` (PICKED, MISSING, etc.)
- **Response**: Updated order object

### `PATCH /api/v1/ops/orders/{order_id}/status`

Update order status.

- **Auth**: Required (Employee, Manager, Admin)
- **Path Params**: `order_id` (UUID)
- **Body**: `{ status }` (OrderStatus enum)
- **Role-based transitions**:
  - Employee:
    - CREATED → IN_PROGRESS
    - IN_PROGRESS → READY (if all picked)
    - IN_PROGRESS → MISSING (if any missing)
  - Manager/Admin: All transitions allowed, including:
    - READY → OUT_FOR_DELIVERY
    - OUT_FOR_DELIVERY → DELIVERED
    - Any status → CANCELED
- **Response**: Updated order object
- **Note**: Employees cannot mark orders as DELIVERED or CANCELED; these require Manager/Admin approval

---

## Stock Requests (Employee/Manager/Admin) (`/api/v1/stock-requests`)

### `POST /api/v1/stock-requests`

Create a new stock request.

- **Auth**: Required (Employee, Manager, Admin)
- **Body**: `{ product_id, branch_id, requested_quantity, reason }`
- **Response**: StockRequest object (201)

### `GET /api/v1/stock-requests/my`

List current user's stock requests.

- **Auth**: Required (Employee, Manager, Admin)
- **Query Params**:
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of stock requests with pagination

### `GET /api/v1/stock-requests/admin`

List all stock requests (for review).

- **Auth**: Required (Manager, Admin)
- **Query Params**:
  - `status` (StockRequestStatus enum, optional)
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of stock requests with pagination

### `GET /api/v1/stock-requests/admin/{request_id}`

Get detailed stock request information.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `request_id` (UUID)
- **Response**: StockRequest object with full details

### `PATCH /api/v1/stock-requests/admin/{request_id}/review`

Review (approve/reject) a stock request.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `request_id` (UUID)
- **Body**: `{ status, approved_quantity, rejection_reason }`
- **Audit**: Old/new inventory values
- **Response**: Updated stock request object

### `PATCH /api/v1/stock-requests/admin/bulk-review`

Review multiple stock requests at once.

- **Auth**: Required (Manager, Admin)
- **Body**: `{ reviews: [{ request_id, status, approved_quantity, rejection_reason }] }`
- **Response**: Array of per-item results (partial success allowed)

---

## Admin - Catalog Management (`/api/v1/admin`)

### `POST /api/v1/admin/categories`

Create a new category.

- **Auth**: Required (Manager, Admin)
- **Body**: `{ name, description }`
- **Response**: Category object (201)

### `PATCH /api/v1/admin/categories/{category_id}`

Update category details.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `category_id` (UUID)
- **Body**: `{ name, description }`
- **Response**: Updated category object

### `PATCH /api/v1/admin/categories/{category_id}/toggle`

Activate/deactivate category (soft delete).

- **Auth**: Required (Manager, Admin)
- **Path Params**: `category_id` (UUID)
- **Query Params**: `active` (boolean)
- **Response**: Updated category object

### `POST /api/v1/admin/products`

Create a new product.

- **Auth**: Required (Manager, Admin)
- **Body**: `{ name, sku, price, category_id, description }`
- **Response**: Product object (201)

### `PATCH /api/v1/admin/products/{product_id}`

Update product details.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `product_id` (UUID)
- **Body**: `{ name, sku, price, category_id, description }` (all optional)
- **Response**: Updated product object

### `PATCH /api/v1/admin/products/{product_id}/toggle`

Activate/deactivate product (soft delete).

- **Auth**: Required (Manager, Admin)
- **Path Params**: `product_id` (UUID)
- **Query Params**: `active` (boolean)
- **Response**: Updated product object

---

## Admin - Branches Management (`/api/v1/admin`)

### `POST /api/v1/admin/branches`

Create a new branch.

- **Auth**: Required (Manager, Admin)
- **Body**: `{ name, address }`
- **Response**: Branch object (201)

### `PATCH /api/v1/admin/branches/{branch_id}`

Update branch details.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `branch_id` (UUID)
- **Body**: `{ name, address }`
- **Response**: Updated branch object

### `PATCH /api/v1/admin/branches/{branch_id}/toggle`

Activate/deactivate branch.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `branch_id` (UUID)
- **Query Params**: `active` (boolean)
- **Response**: Updated branch object

### `POST /api/v1/admin/delivery-slots`

Create a new delivery slot.

- **Auth**: Required (Manager, Admin)
- **Body**: `{ branch_id, day_of_week, start_time, end_time }`
- **Response**: DeliverySlot object (201)

### `PATCH /api/v1/admin/delivery-slots/{slot_id}`

Update delivery slot.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `slot_id` (UUID)
- **Body**: `{ day_of_week, start_time, end_time }`
- **Response**: Updated slot object

### `PATCH /api/v1/admin/delivery-slots/{slot_id}/toggle`

Activate/deactivate delivery slot.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `slot_id` (UUID)
- **Query Params**: `active` (boolean)
- **Response**: Updated slot object

### `GET /api/v1/admin/inventory`

List inventory records across branches.

- **Auth**: Required (Manager, Admin)
- **Query Params**:
  - `branchId` (UUID, optional)
  - `productId` (UUID, optional)
  - `limit` (default: 50)
  - `offset` (default: 0)
- **Response**: Array of inventory records with pagination

### `PUT /api/v1/admin/inventory/{inventory_id}`

Update inventory quantity for a specific branch-product combination.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `inventory_id` (UUID)
- **Body**: `{ quantity, ... }`
- **Audit**: Old/new values recorded
- **Response**: Updated inventory object

---

## Admin - User Management (`/api/v1/admin/users`)

### `GET /api/v1/admin/users`

List all users with optional filters.

- **Auth**: Required (Manager, Admin)
- **Query Params**:
  - `q` (string, optional) - Search by email or full name
  - `role` (CUSTOMER|EMPLOYEE|MANAGER|ADMIN, optional) - Filter by role
  - `isActive` (boolean, optional) - Filter by active status
  - `limit` (default: 50, max: 200)
  - `offset` (default: 0)
- **Response**: Array of users with pagination

### `GET /api/v1/admin/users/{user_id}`

Get detailed user information.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `user_id` (UUID)
- **Response**: User object with full details
- **Errors**: USER_NOT_FOUND (404)

### `PATCH /api/v1/admin/users/{user_id}`

Update user administrative fields.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `user_id` (UUID)
- **Body**: `{ role, is_active, full_name, phone }` (all optional)
- **Audit**: Logs USER_UPDATED with old/new values for ALL changed fields (including profile data)
- **Response**: Updated user object
- **Note**: Allows admin to edit user profile data (full_name, phone) in addition to administrative fields (role, is_active)
- **Errors**:
  - USER_NOT_FOUND (404)
  - CANNOT_MODIFY_SELF_ROLE (403) - Cannot change own role

### `PATCH /api/v1/admin/users/{user_id}/toggle`

Toggle user active status (soft delete). Convenience endpoint; same result as PATCH with `is_active`.

- **Auth**: Required (Manager, Admin)
- **Path Params**: `user_id` (UUID)
- **Query Params**: `active` (boolean, required)
- **Audit**: Logs USER_TOGGLED with old/new status
- **Response**: Updated user object
- **Note**: Follows same pattern as category/product/branch toggle endpoints for consistency
- **Errors**:
  - USER_NOT_FOUND (404)
  - CANNOT_DEACTIVATE_SELF (403) - Cannot deactivate own account

---

## Admin - Audit (`/api/v1/admin/audit`)

### `GET /api/v1/admin/audit`

List audit log entries.

- **Auth**: Required (Manager, Admin)
- **Query Params**:
  - `entityType` (string, optional)
  - `action` (string, optional)
  - `actorId` (UUID, optional)
  - `dateFrom` (ISO datetime, optional)
  - `dateTo` (ISO datetime, optional)
  - `limit` (default: 50, max: 200)
  - `offset` (default: 0)
- **Response**: Array of audit entries with pagination

---

## Health (`/api/v1/health`)

### `GET /api/v1/health`

Health check endpoint (no auth, no rate limit).

- **Auth**: None
- **Response**: `{ status: "ok" }`

---

## Summary

**Total Endpoints**: 60

**By Category**:

- Authentication: 4 endpoints
- Profile & User Management: 6 endpoints (removed duplicate /me/phone)
- Catalog (Public): 5 endpoints
- Branches (Public): 2 endpoints
- Cart: 5 endpoints
- Checkout: 2 endpoints
- Orders (Customer): 3 endpoints
- Operations: 4 endpoints
- Stock Requests: 5 endpoints
- Admin - Catalog: 6 endpoints
- Admin - Branches: 8 endpoints
- Admin - User Management: 4 endpoints
- Admin - Audit: 1 endpoint
- Health: 1 endpoint

**Role-Based Access**:

- **Public** (No Auth): 8 endpoints
- **Customer**: 22 endpoints (auth required)
- **Employee**: 9 endpoints
- **Manager/Admin**: 24+ endpoints (full access)

---

## Notes

1. **Pagination**: Default limit is 50, maximum is 200. List endpoints return `data`, `total`, `limit`, `offset`. Single-item endpoints return only `data`.
2. **Field Naming**: All API requests/responses use **snake_case** (e.g., `cart_id`, `is_active`). Clients using camelCase must convert.
3. **Soft Delete**: Products, categories, branches, and users use `is_active` flag instead of physical deletion.
4. **Ownership**: Customers can only access their own carts and orders (404 for unauthorized access).
5. **Inventory Locking**: Checkout uses pessimistic locking (`FOR UPDATE`) to prevent overselling.
6. **Audit Trail**: All sensitive operations (inventory changes, order status, payments, user role/profile changes) are logged with old/new values.
7. **Idempotency**:
   - Checkout confirm requires `Idempotency-Key` header (not in body)
   - Keys are unique per user and expire after 24 hours
   - Status tracking: IN_PROGRESS → SUCCEEDED/FAILED
   - First request returns 201, duplicate requests return 200
   - Concurrent requests with same key return 409 IDEMPOTENCY_IN_PROGRESS
   - Same key with different payload returns 409 IDEMPOTENCY_KEY_REUSE_MISMATCH
8. **Delivery Source**: All delivery orders deduct from `DELIVERY_SOURCE_BRANCH_ID` branch.
9. **Admin Self-Protection**: Admins cannot modify their own role or deactivate their own account.
10. **Status Transitions**: Employees have limited order status transition permissions; Manager/Admin can perform all transitions including final delivery/cancellation.
11. **Toggle Endpoints**: Provided for consistency across admin resources (categories, products, branches, users). Equivalent to PATCH with `is_active` field.
