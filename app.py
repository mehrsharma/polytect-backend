from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import boto3
import io
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

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

class File(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    uploader_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    classification = db.Column(db.Integer, nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"File(image_id={self.image_id}, uploader_id={self.uploader_id}, date={self.date}, classification={self.classification}, platform={self.platform}, title={self.title})"
    

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

def create_app():
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    # db.init_app(app)
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
            uploader_id = request.form['uploader_id']
            date = datetime.utcnow()
            classification = request.form['classification']
            platform = request.form['platform']
            title = file.filename

            print("image_id: ", image_id)
            print("uploader_id: ", uploader_id)
            print("date: ", date)
            print("classification: ", classification)
            print("platform: ", platform)
            print("title: ", title)
            print("file size", len(file_content))

            new_file = File(image_id=image_id, uploader_id=uploader_id, date=date, classification=classification, platform=platform, title=title)

            s3_uri = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename}"

            s3.upload_fileobj(
                io.BytesIO(file_content),
                S3_BUCKET,
                file.filename,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file.content_type
                }
            )

            db.session.add(new_file)
            db.session.commit()
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

@app.route('/files')
def files():
    files = File.query.all()
    # Convert SQLAlchemy model objects to dictionaries, excluding non-serializable attributes
    file_dicts = [
        {
            'image_id': file.image_id,
            'uploader_id': file.uploader_id,
            'date': file.date.isoformat(),  # Assuming date is a datetime object
            'classification': file.classification,
            'platform': file.platform,
            'title': file.title
        }
        for file in files
    ]
    return jsonify(file_dicts)

@app.route('/files/<int:image_id>')
def file(image_id):
    file = File.query.get(image_id)
    if file is None:
        return jsonify({'error': 'File not found'}), 404
    # Convert SQLAlchemy model object to a dictionary, excluding non-serializable attributes
    file_dict = {
        'image_id': file.image_id,
        'uploader_id': file.uploader_id,
        'date': file.date.isoformat(),  # Assuming date is a datetime object
        'classification': file.classification,
        'platform': file.platform,
        'title': file.title
    }
    return jsonify(file_dict)

# @app.route('/files')
# def files():
#     files = File.query.all()
#     file_dicts = [file.__dict__ for file in files]
#     return jsonify(file_dicts)

# @app.route('/files/<int:image_id>')
# def file(image_id):
#     file = File.query.get(image_id)
#     return jsonify(file.__dict__)

@app.route('/files/<int:image_id>', methods=['DELETE'])
def delete_file(image_id):
    file = File.query.get(image_id)
    db.session.delete(file)
    db.session.commit()
    return jsonify({'message': 'File deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
