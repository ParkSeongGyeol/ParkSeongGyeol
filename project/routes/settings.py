from flask import Blueprint, request, render_template, redirect, url_for
from db import get_db_connection, get_fermentation_settings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE settings SET temperature = ?, humidity = ?, co2 = ?, sugar = ?
            WHERE id = 1
        ''', (
            float(request.form['temperature']),
            int(request.form['humidity']),
            int(request.form['co2']),
            float(request.form['sugar'])
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('main.index'))

    settings = get_fermentation_settings()
    return render_template('settings.html', settings=settings)
