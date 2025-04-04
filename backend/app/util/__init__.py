from flask import Blueprint

util = Blueprint('util', __name__, url_prefix="/util")

from app.util import routes