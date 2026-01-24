# API Request & Response Payloads

This document lists the exact request and response payloads (with types) for all frontend-to-backend API endpoints.

---

## Auth

### POST /api/v1/auth/register

**Request:**

```json
{
  "email": "string (email format)",
  "password": "string (min 8 chars)",
  "full_name": "string",
  "role": "string (Role enum, default: CUSTOMER)"
}
```

**Response:**

```json
{
  "user": {
    "id": "UUID",
    "email": "string",
    "full_name": "string",
    "role": "string"
  },
  "access_token": "string",
  "refresh_token": "string | null",
  "expires_at": "datetime"
}
```

---

### POST /api/v1/auth/login

**Request:**

```json
{
  "email": "string (email format)",
  "password": "string"
}
```

**Response:** Same as register.

---

### POST /api/v1/auth/change-password

**Request:**

```json
{
  "current_password": "string",
  "new_password": "string (min 8 chars)"
}
```

**Response:** (Usually success message or empty, not specified in DTOs.)

---

### POST /api/v1/auth/reset-password

**Request:**

```json
{
  "email": "string (email format)",
  "token": "string",
  "new_password": "string (min 8 chars)"
}
```

**Response:** (Usually success message or empty.)

---

## Cart

### POST/PUT /api/v1/cart/items

**Request:**

```json
{
  "product_id": "UUID",
  "quantity": "int (>0)"
}
```

**Response:**

```json
{
  "id": "UUID",
  "product_id": "UUID",
  "quantity": "int",
  "unit_price": "Decimal"
}
```

### GET /api/v1/cart

**Response:**

```json
{
  "id": "UUID",
  "user_id": "UUID",
  "total_amount": "Decimal",
  "items": [
    {
      "id": "UUID",
      "product_id": "UUID",
      "quantity": "int",
      "unit_price": "Decimal"
    }
  ]
}
```

---

## Checkout

### POST /api/v1/checkout/preview

**Request:**

```json
{
  "cart_id": "UUID",
  "fulfillment_type": "string (DELIVERY|PICKUP)",
  "branch_id": "UUID (optional)",
  "delivery_slot_id": "UUID (optional)",
  "address": "string (optional)"
}
```

**Response:**

```json
{
  "cart_total": "Decimal",
  "delivery_fee": "Decimal | null",
  "missing_items": [
    {
      "product_id": "UUID",
      "requested_quantity": "int",
      "available_quantity": "int"
    }
  ],
  "fulfillment_type": "string"
}
```

### POST /api/v1/checkout/confirm

**Request:**

```json
{
  "cart_id": "UUID",
  "payment_token_id": "UUID",
  "fulfillment_type": "string (optional)",
  "branch_id": "UUID (optional)",
  "delivery_slot_id": "UUID (optional)",
  "address": "string (optional)",
  "save_as_default": "bool (default: false)"
}
```

**Response:**

```json
{
  "order_id": "UUID",
  "order_number": "string",
  "total_paid": "Decimal",
  "payment_reference": "string | null"
}
```

---

## Orders

### GET /api/v1/orders

**Response:**

```json
{
  "orders": [
    {
      "id": "UUID",
      "order_number": "string",
      "total_amount": "Decimal",
      "status": "string",
      "fulfillment_type": "string",
      "created_at": "datetime",
      "items": [
        {
          "product_id": "UUID",
          "name": "string",
          "sku": "string",
          "unit_price": "Decimal",
          "quantity": "int",
          "picked_status": "string"
        }
      ]
    }
  ],
  "pagination": {}
}
```

### POST /api/v1/orders/:id/cancel

**Response:**

```json
{
  "order_id": "UUID",
  "canceled_at": "datetime",
  "status": "string (CANCELED)"
}
```

---

## Ops

### PATCH /api/v1/ops/orders/:id/items/:itemId/picked-status

**Request:**

```json
{
  "picked_status": "string"
}
```

### PATCH /api/v1/ops/orders/:id/status

**Request:**

```json
{
  "status": "string"
}
```

---

## Stock Requests

### POST /api/v1/stock-requests

**Request:**

```json
{
  "branch_id": "UUID",
  "product_id": "UUID",
  "quantity": "int (>0)",
  "request_type": "string"
}
```

**Response:**

```json
{
  "id": "UUID",
  "branch_id": "UUID",
  "product_id": "UUID",
  "quantity": "int",
  "request_type": "string",
  "status": "string",
  "actor_user_id": "UUID",
  "created_at": "datetime"
}
```

### PATCH /api/v1/admin/stock-requests/:id/review

**Request:**

```json
{
  "status": "string",
  "approved_quantity": "int (optional)",
  "rejection_reason": "string (optional)"
}
```

### PATCH /api/v1/admin/stock-requests/bulk-review

**Request:**

```json
{
  "items": [
    {
      "request_id": "UUID",
      "status": "string",
      "approved_quantity": "int (optional)",
      "rejection_reason": "string (optional)"
    }
  ]
}
```

---

## Profile

### PATCH /api/v1/profile/phone

**Request:**

```json
{
  "phone": "string"
}
```

### PATCH /api/v1/profile

**Request:**

```json
{
  "full_name": "string (optional)",
  "phone": "string (optional)"
}
```

### POST /api/v1/profile/address

**Request:**

```json
{
  "address_line": "string",
  "city": "string",
  "postal_code": "string",
  "country": "string",
  "is_default": "bool (default: false)"
}
```

**Response:**

```json
{
  "id": "UUID",
  "user_id": "UUID",
  "address_line": "string",
  "city": "string",
  "postal_code": "string",
  "country": "string",
  "is_default": "bool"
}
```

---

## Admin (Catalog/Branches)

### POST /api/v1/admin/categories

**Request:**

```json
{
  "name": "string",
  "description": "string (optional)"
}
```

### POST /api/v1/admin/products

**Request:**

```json
{
  "name": "string",
  "sku": "string",
  "price": "Decimal",
  "category_id": "UUID",
  "description": "string (optional)"
}
```

### PATCH /api/v1/admin/products/:id

**Request:**

```json
{
  "name": "string (optional)",
  "sku": "string (optional)",
  "price": "Decimal (optional)",
  "category_id": "UUID (optional)"
}
```

### POST /api/v1/admin/branches

**Request:**

```json
{
  "name": "string",
  "address": "string"
}
```

### POST /api/v1/admin/delivery-slots

**Request:**

```json
{
  "branch_id": "UUID",
  "day_of_week": "int (0-6)",
  "start_time": "time",
  "end_time": "time"
}
```

---

## Audit (Admin)

### GET /api/v1/admin/audit

**Query params:**

- entity_type: string (optional)
- action: string (optional)
- actor_user_id: UUID (optional)
- date_from: datetime (optional)
- date_to: datetime (optional)
- limit: int (default 50)
- offset: int (default 0)

**Response:**

```json
{
  "id": "UUID",
  "entity_type": "string",
  "entity_id": "UUID",
  "action": "string",
  "old_value": "object | null",
  "new_value": "object | null",
  "context": "object | null",
  "actor_user_id": "UUID | null",
  "created_at": "datetime"
}
```

---

If you need the full enum values or more details for any specific field, see the backend schemas or ask for a specific endpoint.
