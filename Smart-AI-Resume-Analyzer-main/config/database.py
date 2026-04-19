import sqlite3
import hashlib

# ✅ Database name
DB_NAME = "resume_data_v2.db"


def get_database_connection():
    return sqlite3.connect(DB_NAME)


# ✅ Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ✅ Initialize database (SAFE — no data loss)
def init_database():
    conn = get_database_connection()
    cursor = conn.cursor()

    # ✅ Create tables ONLY if not exist (NO DROP)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        linkedin TEXT,
        github TEXT,
        portfolio TEXT,
        summary TEXT,
        target_role TEXT,
        target_category TEXT,
        education TEXT,
        experience TEXT,
        projects TEXT,
        skills TEXT,
        template TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        ats_score REAL,
        keyword_match_score REAL,
        format_score REAL,
        section_score REAL,
        missing_skills TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_email TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        model_used TEXT,
        resume_score INTEGER,
        job_role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


# ✅ Add admin
def add_admin(email, password):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute(
            'INSERT INTO admin (email, password) VALUES (?, ?)',
            (email, hashed_password)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding admin: {e}")
        return False
    finally:
        conn.close()


# ✅ Verify admin
def verify_admin(email, password):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute(
            'SELECT * FROM admin WHERE email=? AND password=?',
            (email, hashed_password)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


# ✅ Save resume
def save_resume_data(data):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        personal_info = data.get('personal_info', {})

        cursor.execute('''
        INSERT INTO resume_data (
            name, email, phone, linkedin, github, portfolio,
            summary, target_role, target_category, education,
            experience, projects, skills, template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            personal_info.get('full_name', ''),
            personal_info.get('email', ''),
            personal_info.get('phone', ''),
            personal_info.get('linkedin', ''),
            personal_info.get('github', ''),
            personal_info.get('portfolio', ''),
            data.get('summary', ''),
            data.get('target_role', ''),
            data.get('target_category', ''),
            str(data.get('education', [])),
            str(data.get('experience', [])),
            str(data.get('projects', [])),
            str(data.get('skills', [])),
            data.get('template', '')
        ))

        conn.commit()
        return cursor.lastrowid

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return None

    finally:
        conn.close()


# ✅ Save analysis
def save_analysis_data(resume_id, analysis):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO resume_analysis (
            resume_id, ats_score, keyword_match_score,
            format_score, section_score, missing_skills,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            float(analysis.get('ats_score', 0)),
            float(analysis.get('keyword_match_score', 0)),
            float(analysis.get('format_score', 0)),
            float(analysis.get('section_score', 0)),
            analysis.get('missing_skills', ''),
            analysis.get('recommendations', '')
        ))

        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        conn.close()


# ✅ Log admin action
def log_admin_action(admin_email, action):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO admin_logs (admin_email, action) VALUES (?, ?)',
            (admin_email, action)
        )
        conn.commit()
    finally:
        conn.close()
