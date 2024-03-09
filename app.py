from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import boto3
import io
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

S3_BUCKET = 'vincent-testing'
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_REGION = 'us-east-1'

s3 = boto3.client(
   's3',
   aws_access_key_id=S3_ACCESS_KEY,
   aws_secret_access_key=S3_SECRET_KEY,
   region_name=S3_REGION
)

def create_app():
    return app

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_content = file.read()
    print("file size outside", len(file_content))
    
    try:
        if request.method == 'POST':
            image_id = hash(file_content)

            s3_uri = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename+str(image_id)}"

            s3.upload_fileobj(
                io.BytesIO(file_content),
                S3_BUCKET,
                file.filename+str(image_id),
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file.content_type
                }
            )

            return jsonify({'message': 'Upload successful', 's3_uri': s3_uri}), 201
    except IntegrityError:
        return jsonify({'error': 'File already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('', filename)

@app.route('/')
def index():
    return 'Hello, World 0!'

if __name__ == '__main__':
    app.run(debug=True)
