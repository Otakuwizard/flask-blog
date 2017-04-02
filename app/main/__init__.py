from flask import Bluerpint

main = Blueprint('main', __name__)

from . import views, errors