from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

upload_image_blueprint = Blueprint('upload_image', __name__)


@upload_image_blueprint.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.root_path, 'static\\uploaded_images', filename)
        file.save(filepath)
        return jsonify({'location': '/static/uploaded_images/' + filename}), 200


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
