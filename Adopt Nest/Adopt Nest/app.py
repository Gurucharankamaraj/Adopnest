import os
import logging
import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-change-in-production")

# File upload configuration
from health_upload import health_upload_bp
app.register_blueprint(health_upload_bp)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", "#Moni1805"),
            database=os.environ.get("MYSQL_DB", "adoptnest"),
            port=int(os.environ.get("MYSQL_PORT", 3306))
        )
        return connection
    except mysql.connector.Error as err:
        app.logger.error(f"MySQL connection error: {err}")
        return None


def init_database():
    connection = get_db_connection()
    if not connection:
        app.logger.error("Failed to connect to database for initialization")
        return

    cursor = connection.cursor()
    try:
        # Create adoption_requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adoption_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                pet_id VARCHAR(50) NOT NULL,
                reason TEXT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)


        try:
            cursor.execute("CREATE INDEX idx_status ON adoption_requests (status)")
        except mysql.connector.Error as e:
            if "Duplicate key name" not in str(e):
                raise
            
        try:
            cursor.execute("CREATE INDEX idx_pet_id ON adoption_requests (pet_id)")
        except mysql.connector.Error as e:
            if "Duplicate key name" not in str(e):
                raise

        try:
            cursor.execute("CREATE INDEX idx_request_date ON adoption_requests (request_date)")
        except mysql.connector.Error as e:
            if "Duplicate key name" not in str(e):
                raise


        # Create health_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pet_id VARCHAR(50) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pet_id_health ON health_records (pet_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_upload_date_health ON health_records (upload_date)")

        connection.commit()
        app.logger.info("Database tables initialized successfully")

    except mysql.connector.Error as err:
        connection.rollback()
        app.logger.error(f"Error initializing database: {err}")
    finally:
        cursor.close()
        connection.close()



# Initialize database on startup
init_database()

# Serve static HTML files
@app.route('/')
def index():
    return send_file('attached_assets/index_1753355929778.html')

@app.route('/browse.html')
def browse():
    return send_file('attached_assets/browse_1753355929772.html')

@app.route('/adopt.html')
def adopt():
    return send_file('adoption_form.html')

@app.route('/tracker.html')
def tracker():
    return send_file('tracker_dynamic.html')

@app.route('/blog.html')
def blog():
    return send_file('attached_assets/blog_1753355929770.html')

@app.route('/health.html')
def health():
    return send_file('health.html')

# Serve CSS and JS files
@app.route('/browser_style.css')
def browser_style():
    return send_file('attached_assets/browser_style_1753355929773.css')

@app.route('/script.js')
def script():
    return send_file('attached_assets/script_1753355929780.js')

@app.route('/index_style.css')
def index_style():
    return send_file('attached_assets/index_style_1753355929779.css')

@app.route('/health_style.css')
def health_style():
    return send_file('attached_assets/health_style_1753355929777.css')





# Routes for adoption requests (existing functionality)
@app.route('/submit_adoption', methods=['POST'])
def submit_adoption():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    pet_id = data.get('pet_id')
    reason = data.get('reason')

    if not all([name, email, pet_id, reason]):
        return jsonify({"error": "All fields are required"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor()
    try:
        query = """
            INSERT INTO adoption_requests (name, email, pet_id, reason, status)
            VALUES (%s, %s, %s, %s, 'pending')
        """
        cursor.execute(query, (name, email, pet_id, reason))
        connection.commit()
        app.logger.info(f"Inserted {cursor.rowcount} adoption request row(s)")
        return jsonify({"message": "Adoption request submitted successfully"}), 201
    except mysql.connector.Error as err:
        connection.rollback()
        app.logger.error(f"Error inserting adoption request: {err}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/get_requests', methods=['GET'])
def get_requests():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM adoption_requests ORDER BY request_date DESC")
        rows = cursor.fetchall()
        return jsonify([dict(row) for row in rows]), 200
    except mysql.connector.Error as err:
        app.logger.error(f"Error fetching adoption requests: {err}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        cursor.close()
        connection.close()





# Admin authentication routes (No DB)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin_login.html')

        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))


# Admin panel route
@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_login'))

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM adoption_requests ORDER BY request_date DESC")
        requests = cursor.fetchall()
        return render_template('admin_panel.html', requests=requests)
    except mysql.connector.Error as err:
        app.logger.error(f"Error loading adoption requests: {err}")
        flash('Error loading adoption requests', 'error')
        return render_template('admin_panel.html', requests=[])
    finally:
        cursor.close()
        connection.close()


@app.route('/admin/update_request', methods=['POST'])
def update_request_status():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    request_id = request.form.get('request_id')
    new_status = request.form.get('status')

    if not request_id or not new_status:
        flash('Request ID and status are required', 'error')
        return redirect(url_for('admin_panel'))

    if new_status not in ['pending', 'approved', 'rejected']:
        flash('Invalid status', 'error')
        return redirect(url_for('admin_panel'))

    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_panel'))

    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE adoption_requests SET status = %s, updated_date = CURRENT_TIMESTAMP WHERE id = %s",
            (new_status, request_id)
        )
        connection.commit()
        if cursor.rowcount > 0:
            flash(f"Request status updated to {new_status}", "success")
        else:
            flash("Request not found", "error")
    except mysql.connector.Error as err:
        connection.rollback()
        app.logger.error(f"Error updating request status: {err}")
        flash("Error updating request status", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_panel'))





if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
