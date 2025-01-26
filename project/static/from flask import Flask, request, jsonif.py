from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def save_data():
    data = request.json
    temperature = data['temperature']
    humidity = data['humidity']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO environment (temperature, humidity) VALUES (?, ?)",
        (temperature, humidity)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Data saved!"}), 200

if __name__ == '__main__':
    app.run(debug=True)