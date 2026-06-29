import os

class Config:
    # MySQL config
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'Mitali526@'  # ⚠️ apna password daalo
    MYSQL_DB = 'resume_parser'
    
    # File upload config
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    SECRET_KEY = os.urandom(24)