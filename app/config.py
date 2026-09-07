import os
import shutil

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jig-jharkhand-innovation-grid-secret-key-2026')
    
    # Handle cloud serverless environments (Vercel) vs persistent servers (Render/Local)
    if os.environ.get('VERCEL'):
        tmp_db = '/tmp/jig.sqlite'
        orig_db = os.path.join(os.path.dirname(basedir), 'instance', 'jig.sqlite')
        if not os.path.exists(tmp_db) and os.path.exists(orig_db):
            try:
                shutil.copyfile(orig_db, tmp_db)
            except Exception:
                pass
        default_db = f"sqlite:///{tmp_db}"
        default_upload = '/tmp/uploads'
    else:
        default_db = f"sqlite:///{os.path.join(os.path.dirname(basedir), 'instance', 'jig.sqlite')}"
        default_upload = os.path.join(basedir, 'static', 'uploads')

    # Fix for Postgres URLs if using Supabase/Neon/Render PostgreSQL (postgres:// -> postgresql://)
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = raw_db_url or default_db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = default_upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
