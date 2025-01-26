from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_db_connection

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/data', methods=['POST'])
def save_data():
    data = request.json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO environment (timestamp, temperature, humidity, co2, density, alcohol, sugar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        data.get('temperature'),
        data.get('humidity'),
        data.get('co2'),
        data.get('density'),
        data.get('alcohol'),
        data.get('sugar')
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data saved!"}), 200
