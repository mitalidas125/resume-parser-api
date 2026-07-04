from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import Config
import os
from werkzeug.utils import secure_filename
import PyPDF2
import spacy

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

nlp = spacy.load("en_core_web_sm")

SKILLS_LIST = [
    "python", "flask", "django", "mysql", "sql", "javascript",
    "html", "css", "git", "github", "rest api", "api",
    "machine learning", "data analysis", "pandas", "numpy",
    "web scraping", "beautifulsoup", "selenium", "linux",
    "mongodb", "postgresql", "docker", "aws", "spacy"
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(filepath):
    try:
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise ValueError(f"PDF read error: {str(e)}")

def extract_skills(text):
    try:
        text_lower = text.lower()
        found_skills = []
        for skill in SKILLS_LIST:
            if skill in text_lower:
                found_skills.append(skill)
        return found_skills
    except Exception as e:
        raise ValueError(f"Skills extract error: {str(e)}")

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "File too large! Max size 16MB"}), 413

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
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file found"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files allowed"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = extract_text_from_pdf(filepath)
        skills = extract_skills(text)

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO resumes (name, skills) VALUES (%s, %s)",
            ('Unknown', ','.join(skills))
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({
            "message": "Resume uploaded and parsed!",
            "filename": filename,
            "extracted_skills": skills,
            "total_skills_found": len(skills)
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

@app.route('/jobs', methods=['GET'])
def get_jobs():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM jobs")
        jobs = cur.fetchall()
        cur.close()

        jobs_list = []
        for job in jobs:
            jobs_list.append({
                "id": job[0],
                "title": job[1],
                "company": job[2],
                "required_skills": job[3].split(','),
                "created_at": str(job[4])
            })

        return jsonify({
            "total_jobs": len(jobs_list),
            "jobs": jobs_list
        })
    except Exception as e:
        return jsonify({"error": "Could not fetch jobs", "details": str(e)}), 500

@app.route('/match', methods=['POST'])
def match_jobs():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file found"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files allowed"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = extract_text_from_pdf(filepath)
        resume_skills = extract_skills(text)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM jobs")
        jobs = cur.fetchall()
        cur.close()

        matched_jobs = []
        for job in jobs:
            job_skills = job[3].split(',')
            matched = [s for s in resume_skills if s in job_skills]
            score = round((len(matched) / len(job_skills)) * 100, 2)

            matched_jobs.append({
                "title": job[1],
                "company": job[2],
                "required_skills": job_skills,
                "matched_skills": matched,
                "match_score": f"{score}%"
            })

        matched_jobs = sorted(matched_jobs, key=lambda x: float(x['match_score'].replace('%', '')), reverse=True)

        return jsonify({
            "resume_skills": resume_skills,
            "total_jobs_checked": len(matched_jobs),
            "job_matches": matched_jobs
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)