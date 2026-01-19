"""Blueprint placeholder for admin."""
from flask import Blueprint

blueprint = Blueprint('admin', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for admin'}
