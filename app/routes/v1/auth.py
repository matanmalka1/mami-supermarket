"""Blueprint placeholder for auth."""
from flask import Blueprint

blueprint = Blueprint('auth', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for auth'}
