from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import Config
import os
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(filepath):
    text = ""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

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
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # PDF se text extract karo
        text = extract_text_from_pdf(filepath)
        
        return jsonify({
            "message": "Resume uploaded and parsed!",
            "filename": filename,
            "extracted_text": text[:500]  # Pehle 500 characters dikhayenge
        }), 201
    
    return jsonify({"error": "Only PDF files allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)