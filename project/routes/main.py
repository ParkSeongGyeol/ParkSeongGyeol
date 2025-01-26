from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    from project.db import get_fermentation_settings  # 함수 내부에서 import
    settings = get_fermentation_settings()
    return render_template('index.html', settings=settings)
