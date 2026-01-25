"""Minimal coverage for the catalog reviews stub."""

from app.models import Product

def test_catalog_product_reviews_empty(client, session):
    product = session.query(Product).first()
    response = client.get(f"/api/v1/catalog/products/{product.id}/reviews")
    assert response.status_code == 200
    assert response.get_json()["data"]["items"] == []
