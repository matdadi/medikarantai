from flask import Blueprint, render_template

public_bp = Blueprint("main", __name__)

# default endpoint
@public_bp.route("/")
def index():
    return render_template("public/index.html")