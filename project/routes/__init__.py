from flask import Blueprint
from .main import main_bp
from .api import api_bp
from .settings import settings_bp

def init_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)
