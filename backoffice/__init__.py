from flask import Blueprint

backoffice_bp = Blueprint("backoffice", __name__, template_folder="templates")

from . import routes
