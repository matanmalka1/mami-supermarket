"""Blueprint placeholder for orders."""
from flask import Blueprint

blueprint = Blueprint('orders', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for orders'}
