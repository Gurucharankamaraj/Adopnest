# backend.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Setup database connection pool
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="adoptnest",
    autocommit=False  # work explicitly with commits
)

@app.route('/submit_adoption', methods=['POST'])
def submit_adoption():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    pet_id = data.get('pet_id')
    reason = data.get('reason')

    if not all([name, email, pet_id, reason]):
        return jsonify({"error": "All fields are required"}), 400

    cursor = db.cursor()
    try:
        query = """
            INSERT INTO pets (name, email, pet_id, reason)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, pet_id, reason))
        db.commit()
        app.logger.info(f"Inserted {cursor.rowcount} row(s)")
        return jsonify({"message": "Adoption request submitted successfully"}), 201
    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Error inserting data: {err}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        cursor.close()

@app.route('/get_requests', methods=['GET'])
def get_requests():
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM pets ORDER BY request_date DESC")
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except mysql.connector.Error as err:
        app.logger.error(f"Error fetching data: {err}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        cursor.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)