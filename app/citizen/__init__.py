from flask import Blueprint

citizen_bp = Blueprint('citizen', __name__)

from app.citizen import routes
