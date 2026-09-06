from flask import Blueprint

university_bp = Blueprint('university', __name__)

from app.university import routes
