# Resume Parser & Job Matcher API

A REST API built with Flask and MySQL that parses resumes and matches them with job listings based on skills.

## Tech Stack
- Python 3
- Flask
- MySQL
- PyPDF2
- spaCy
- REST API

## Features
- Upload PDF resume and extract text
- Auto-detect skills from resume
- Match resume with job listings
- Score each job based on skill match percentage

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API status |
| GET | /health | Health check |
| GET | /jobs | Get all jobs |
| POST | /upload | Upload and parse resume |
| POST | /match | Match resume with jobs |

## Setup Instructions

1. Clone the repository
   git clone https://github.com/mitalidas125/resume-parser-api.git

2. Create virtual environment
   python -m venv venv
   venv\Scripts\activate

3. Install dependencies
   pip install -r requirements.txt

4. Setup MySQL database
   CREATE DATABASE resume_parser;

5. Update config.py with your MySQL password

6. Run the app
   python app.py

## Sample Response - Job Match

{
  "resume_skills": ["python", "django", "sql"],
  "total_jobs_checked": 5,
  "job_matches": [
    {
      "company": "Infosys",
      "match_score": "100.0%",
      "title": "Backend Developer"
    }
  ]
}

## Author
Mitali Das
BCA Graduate | Python Backend Developer
GitHub: github.com/mitalidas125