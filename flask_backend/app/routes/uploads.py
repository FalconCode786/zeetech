"""File upload routes"""

from flask import Blueprint, request, current_app, send_file
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@uploads_bp.route('', methods=['POST'])
@login_required
def upload_file():
    """Upload a file (profile picture or service image)"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return {'error': 'No file provided', 'code': 'MISSING_FILE'}, 400

        file = request.files['file']

        if file.filename == '':
            return {'error': 'No file selected', 'code': 'NO_FILE'}, 400

        if not allowed_file(file.filename):
            return {'error': 'File type not allowed', 'code': 'INVALID_FILE_TYPE'}, 400

        # Check file size (max 16MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16777216)
        if file_length > max_size:
            return {'error': 'File too large', 'code': 'FILE_TOO_LARGE'}, 413

        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{int(datetime.now().timestamp())}.{ext}"

        # Create uploads directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)

        # Generate file URL
        file_url = f"/uploads/{unique_filename}"

        return {
            'message': 'File uploaded successfully',
            'data': {
                'url': file_url,
                'filename': unique_filename,
                'originalFilename': secure_filename(file.filename),
                'size': file_length,
                'uploadedAt': datetime.now().isoformat()
            }
        }, 201

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@uploads_bp.route('/<filename>', methods=['GET'])
def download_file(filename):
    """Download an uploaded file"""
    try:
        # Validate filename to prevent directory traversal
        filename = secure_filename(filename)

        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)

        # Check if file exists
        if not os.path.exists(filepath):
            return {'error': 'File not found', 'code': 'NOT_FOUND'}, 404

        # Check if path is within upload folder (security check)
        if not os.path.abspath(filepath).startswith(os.path.abspath(upload_folder)):
            return {'error': 'Invalid file path', 'code': 'INVALID_PATH'}, 400

        return send_file(filepath, as_attachment=False)

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@uploads_bp.route('/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    """Delete an uploaded file"""
    try:
        # Validate filename
        filename = secure_filename(filename)

        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)

        # Check if file exists
        if not os.path.exists(filepath):
            return {'error': 'File not found', 'code': 'NOT_FOUND'}, 404

        # Check if path is within upload folder
        if not os.path.abspath(filepath).startswith(os.path.abspath(upload_folder)):
            return {'error': 'Invalid file path', 'code': 'INVALID_PATH'}, 400

        # Delete file
        os.remove(filepath)

        return {'message': 'File deleted successfully'}, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
