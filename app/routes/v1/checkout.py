"""Blueprint placeholder for checkout."""
from flask import Blueprint

blueprint = Blueprint('checkout', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for checkout'}
