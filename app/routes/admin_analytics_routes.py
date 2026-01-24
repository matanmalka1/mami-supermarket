"""Admin analytics: revenue endpoint (sum of completed orders, grouped by day/month)."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role, OrderStatus
from app.extensions import db
import sqlalchemy as sa
from datetime import datetime, timedelta
from decimal import Decimal

blueprint = Blueprint("admin_analytics", __name__)

@blueprint.get("/revenue")
@jwt_required()
@require_role(Role.ADMIN)
def revenue():
    range_ = request.args.get("range", "30d")
    granularity = request.args.get("granularity")
    now = datetime.utcnow()
    if range_ == "12m":
        start = now.replace(day=1, month=now.month, year=now.year) - timedelta(days=365)
        gran = "month"
    elif range_ == "90d":
        start = now - timedelta(days=90)
        gran = "day"
    else:
        start = now - timedelta(days=30)
        gran = "day"
    if granularity:
        gran = granularity

    # Detect SQLite for test environment compatibility
    is_sqlite = hasattr(db, 'engine') and db.engine and db.engine.dialect.name == "sqlite"
    if is_sqlite:
        if gran == "month":
            label_expr = sa.func.strftime('%Y-%m', sa.column('created_at'))
        else:
            label_expr = sa.func.strftime('%Y-%m-%d', sa.column('created_at'))
    else:
        if gran == "month":
            label_expr = sa.func.to_char(sa.func.date_trunc('month', sa.column('created_at')), 'YYYY-MM')
        else:
            label_expr = sa.func.to_char(sa.func.date_trunc('day', sa.column('created_at')), 'YYYY-MM-DD')

    q = sa.select(
        label_expr.label("label"),
        sa.func.coalesce(sa.func.sum(sa.cast(sa.column('total_amount'), sa.Numeric(12,2))), 0).label("value")
    ).select_from(sa.text('orders')).where(
        sa.text("status = 'COMPLETED' AND created_at >= :start")
    ).group_by(label_expr).order_by(label_expr)
    result = db.session.execute(q, {"start": start}).fetchall()
    labels = [row.label for row in result]
    values = [float(row.value) for row in result]
    return jsonify({"data": {"labels": labels, "values": values}})
