from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import Config
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# Helper function - file allowed hai ya nahi
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return jsonify({
        "message": "Resume Parser API is running!",
        "version": "1.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE()")
        data = cur.fetchone()
        cur.close()
        return jsonify({
            "status": "Database connected!",
            "database": data[0]
        })
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_resume():
    # File hai request mein?
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    
    file = request.files['file']
    
    # File select ki hai?
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # PDF hai?
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            "message": "Resume uploaded successfully!",
            "filename": filename,
            "filepath": filepath
        }), 201
    
    return jsonify({"error": "Only PDF files allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)