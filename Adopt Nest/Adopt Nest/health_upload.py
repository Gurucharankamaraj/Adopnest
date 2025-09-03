# health_upload.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.utils import secure_filename

health_upload_bp = Blueprint('health_upload_bp', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@health_upload_bp.route('/submit_health_record', methods=['POST'])
def submit_health_record():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"

        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)

        try:
            file.save(file_path)
            app.logger.info(f"File saved to: {file_path}")
            return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 201
        except Exception as e:
            app.logger.error(f"Failed to save file: {e}")
            return jsonify({"error": "File upload failed"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400
