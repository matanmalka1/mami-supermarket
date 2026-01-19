"""Blueprint placeholder for ops."""
from flask import Blueprint

blueprint = Blueprint('ops', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for ops'}
