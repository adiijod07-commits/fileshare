from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import mimetypes
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# -----------------------------
# Folders
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.abspath(
    os.path.join(BASE_DIR, "..", "storage")
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Home
# -----------------------------

@app.route("/")
def home():
    return "FileShare Backend is Running!"


# -----------------------------
# Upload File
# -----------------------------

@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({
            "error": "No file selected"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    # Original filename
    original_filename = file.filename

    # Remove unsafe path parts but keep normal filename/extension
    filename = os.path.basename(original_filename)

    # Extra safety
    filename = secure_filename(filename)

    if filename == "":
        return jsonify({
            "error": "Invalid filename"
        }), 400

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    # Save file
    file.save(file_path)

    # Create download URL using the current server address
    base_url = request.host_url.rstrip("/")
    download_url = (
        f"{base_url}/download/{quote(filename)}"
    )

    return jsonify({
        "message": "File uploaded successfully!",
        "filename": filename,
        "download_url": download_url
    })


# -----------------------------
# Download File
# -----------------------------

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):

    filename = os.path.basename(filename)

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    # File does not exist
    if not os.path.isfile(file_path):
        return jsonify({
            "error": "File not found"
        }), 404

    # Detect file type
    mimetype, _ = mimetypes.guess_type(filename)

    if mimetype is None:
        mimetype = "application/octet-stream"

    # Send original file with original filename
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename,
        conditional=True
    )


# -----------------------------
# Run Server
# -----------------------------

if __name__ == "__main__":

    print("----------------------------------------")
    print("        FileShare Backend")
    print("----------------------------------------")
    print("Storage folder:")
    print(UPLOAD_FOLDER)
    print()
    print("Server:")
    print("http://127.0.0.1:5000")
    print()
    print("For phone/network access:")
    print("Use your PC's IPv4 address + :5000")
    print("----------------------------------------")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
