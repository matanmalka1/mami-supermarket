import uuid
import pytest
import sqlalchemy as sa
from decimal import Decimal

from app.middleware.error_handler import DomainError
from app.models import Audit, Cart, CartItem, Order, OrderItem, StockRequest
from app.models.enums import FulfillmentType, OrderStatus, PickedStatus, Role, StockRequestStatus, StockRequestType
from app.schemas.checkout import CheckoutConfirmRequest, CheckoutPreviewRequest
from app.schemas.stock_requests import BulkReviewItem, BulkReviewRequest
from app.services.checkout import CheckoutService
from app.services.ops import OpsOrderService
from app.services.order import OrderService
from app.services.stock_requests import StockRequestService
from app.extensions import db


def _build_cart(session, user_id, product_id, qty, price):
    cart = Cart(user_id=user_id)
    session.add(cart)
    session.flush()
    item = CartItem(
        cart_id=cart.id,
        product_id=product_id,
        quantity=qty,
        unit_price=price,
    )
    session.add(item)
    session.commit()
    return cart


def test_checkout_insufficient_stock(session, test_app, users, product_with_inventory):
    user, _ = users
    product, _, _ = product_with_inventory
    cart = _build_cart(session, user.id, product.id, qty=2, price=Decimal("10.00"))
    payload = CheckoutConfirmRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=product_with_inventory[2].id,
        delivery_slot_id=None,
        address=None,
        payment_token_id=uuid.uuid4(),
        save_as_default=False,
        idempotency_key="k1",
    )
    with pytest.raises(DomainError) as exc:
        CheckoutService.confirm(payload)
    assert exc.value.code == "INSUFFICIENT_STOCK"


def test_checkout_preview_branch_switch_missing(session, users, product_with_inventory):
    user, _ = users
    product, _, other_branch = product_with_inventory
    cart = _build_cart(session, user.id, product.id, qty=1, price=Decimal("10.00"))
    payload = CheckoutPreviewRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=other_branch.id,
    )
    preview = CheckoutService.preview(payload)
    assert preview.missing_items, "Expected missing items when branch has no stock"


def test_order_ownership_returns_404(session, users, product_with_inventory):
    user1, user2 = users
    product, _, _ = product_with_inventory
    order = Order(
        user_id=user1.id,
        order_number="ORD1",
        total_amount=Decimal("10.00"),
        fulfillment_type=FulfillmentType.PICKUP,
        status=OrderStatus.CREATED,
    )
    session.add(order)
    session.flush()
    session.add(OrderItem(order_id=order.id, product_id=product.id, name="Milk", sku="SKU1", unit_price=Decimal("10.00"), quantity=1))
    session.commit()
    with pytest.raises(DomainError) as exc:
        OrderService.get_order(order.id, user2.id)
    assert exc.value.code == "NOT_FOUND"


def test_employee_invalid_status_transition(session, users, product_with_inventory):
    user, _ = users
    product, _, _ = product_with_inventory
    order = Order(
        user_id=user.id,
        order_number="ORD2",
        total_amount=Decimal("10.00"),
        fulfillment_type=FulfillmentType.PICKUP,
        status=OrderStatus.CREATED,
    )
    session.add(order)
    session.flush()
    session.add(OrderItem(order_id=order.id, product_id=product.id, name="Milk", sku="SKU1", unit_price=Decimal("10.00"), quantity=1))
    session.commit()
    with pytest.raises(DomainError) as exc:
        OpsOrderService.update_order_status(order.id, OrderStatus.READY.value, user.id, Role.EMPLOYEE)
    assert exc.value.code == "INVALID_STATUS_TRANSITION"


def test_missing_items_flow_sets_missing(session, users, product_with_inventory):
    user, _ = users
    product, _, _ = product_with_inventory
    order = Order(
        user_id=user.id,
        order_number="ORD3",
        total_amount=Decimal("10.00"),
        fulfillment_type=FulfillmentType.PICKUP,
        status=OrderStatus.IN_PROGRESS,
    )
    session.add(order)
    session.flush()
    session.add(OrderItem(order_id=order.id, product_id=product.id, name="Milk", sku="SKU1", unit_price=Decimal("10.00"), quantity=1, picked_status=PickedStatus.MISSING))
    session.commit()
    updated = OpsOrderService.update_order_status(order.id, OrderStatus.MISSING.value, user.id, Role.EMPLOYEE)
    assert updated.status == OrderStatus.MISSING


def test_bulk_review_partial_success(session, users, product_with_inventory):
    user, _ = users
    product, inv, _ = product_with_inventory
    req = StockRequest(
        branch_id=inv.branch_id,
        product_id=product.id,
        quantity=1,
        request_type=StockRequestType.ADD_QUANTITY,
        status=StockRequestStatus.PENDING,
        actor_user_id=user.id,
    )
    session.add(req)
    session.commit()
    payload = BulkReviewRequest(
        items=[
            BulkReviewItem(request_id=req.id, status=StockRequestStatus.APPROVED, approved_quantity=2),
            BulkReviewItem(request_id=uuid.uuid4(), status=StockRequestStatus.APPROVED, approved_quantity=2),
        ]
    )
    results = StockRequestService.bulk_review(payload, user.id)
    assert any(r["result"] == "ok" for r in results)
    assert any(r["result"] == "error" for r in results)


def test_no_audit_on_failed_review(session, users):
    user, _ = users
    with pytest.raises(DomainError):
        StockRequestService.review(
            request_id=uuid.uuid4(),
            status=StockRequestStatus.APPROVED,
            approved_quantity=1,
            rejection_reason=None,
            actor_id=user.id,
        )
    audits = db.session.execute(sa.select(sa.func.count()).select_from(Audit)).scalar()
    assert audits == 0


def test_payment_danger_zone_logged(session, test_app, users, product_with_inventory, monkeypatch):
    user, _ = users
    product, inv, _ = product_with_inventory
    # replenish inventory for this test
    inv.available_quantity = 5
    session.add(inv)
    session.commit()
    cart = _build_cart(session, user.id, product.id, qty=1, price=Decimal("10.00"))
    payload = CheckoutConfirmRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=inv.branch_id,
        delivery_slot_id=None,
        address=None,
        payment_token_id=uuid.uuid4(),
        save_as_default=False,
        idempotency_key="danger",
    )

    def _fail_store(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("app.services.payment.PaymentService.charge", lambda *_args, **_kw: "ref123")
    monkeypatch.setattr("app.services.checkout.CheckoutService._store_idempotency", _fail_store)

    with pytest.raises(RuntimeError):
        CheckoutService.confirm(payload)
    audit_rows = db.session.execute(
        sa.select(Audit).where(Audit.action == "PAYMENT_CAPTURED_NOT_COMMITTED")
    ).scalars().all()
    assert audit_rows, "Expected danger zone audit log when commit fails after payment"
