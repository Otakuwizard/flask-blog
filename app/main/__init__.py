from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor
def jinject_permission():
    return dict(Permission=Permission)