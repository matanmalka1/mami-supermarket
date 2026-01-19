"""Blueprint placeholder for cart."""
from flask import Blueprint

blueprint = Blueprint('cart', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for cart'}
