from flask import Blueprint

government_bp = Blueprint('government', __name__)

from app.government import routes
