from flask import Flask, request, jsonify, send_file
import boto3
import logging
import os

app = Flask(__name__)
MINIO_URL = os.getenv("MINIO_URL", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin123")
BUCKET_NAME = "file-storage"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

logging.basicConfig(level=logging.INFO)

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    file_name = file.filename
    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, file_name)
        logging.info(f"File '{file_name}' uploaded successfully.")
        return jsonify({"message": f"File '{file_name}' uploaded successfully."})
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        file_path = f"/tmp/{file_id}"
        s3_client.download_file(BUCKET_NAME, file_id, file_path)
        logging.info(f"File '{file_id}' downloaded successfully.")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/update/<file_id>", methods=["PUT"])
def update_file(file_id):
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, file_id)
        logging.info(f"File '{file_id}' updated successfully.")
        return jsonify({"message": f"File '{file_id}' updated successfully."})
    except Exception as e:
        logging.error(f"Error updating file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_id)
        logging.info(f"File '{file_id}' deleted successfully.")
        return jsonify({"message": f"File '{file_id}' deleted successfully."})
    except Exception as e:
        logging.error(f"Error deleting file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
