from flask import Blueprint

perm_api_blueprint = Blueprint('perm_api', __name__)

from . import routes