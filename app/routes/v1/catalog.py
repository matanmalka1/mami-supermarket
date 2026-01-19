"""Blueprint placeholder for catalog."""
from flask import Blueprint

blueprint = Blueprint('catalog', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for catalog'}
