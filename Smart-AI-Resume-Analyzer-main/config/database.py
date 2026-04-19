import sqlite3
import hashlib

# ✅ Central DB name (easy to change anytime)
DB_NAME = "resume_data_v2.db"


def get_database_connection():
    return sqlite3.connect(DB_NAME)


# ✅ Hash password (security improvement)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ✅ Initialize fresh database (always clean start)
def init_database():
    conn = get_database_connection()
    cursor = conn.cursor()

    # 🔴 DROP all tables (full reset)
    cursor.execute("DROP TABLE IF EXISTS resume_data")
    cursor.execute("DROP TABLE IF EXISTS resume_skills")
    cursor.execute("DROP TABLE IF EXISTS resume_analysis")
    cursor.execute("DROP TABLE IF EXISTS admin_logs")
    cursor.execute("DROP TABLE IF EXISTS admin")
    cursor.execute("DROP TABLE IF EXISTS ai_analysis")

    # ✅ Create resume_data table
    cursor.execute('''
    CREATE TABLE resume_data (
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

    # ✅ Create resume_analysis table
    cursor.execute('''
    CREATE TABLE resume_analysis (
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

    # ✅ Create admin_logs table
    cursor.execute('''
    CREATE TABLE admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_email TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ✅ Create admin table (with hashed password)
    cursor.execute('''
    CREATE TABLE admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ✅ Create AI analysis table
    cursor.execute('''
    CREATE TABLE ai_analysis (
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


# ✅ Reset DB anytime
def reset_database():
    init_database()


# ✅ Add admin (with hashed password)
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


# ✅ Verify admin login
def verify_admin(email, password):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute(
            'SELECT * FROM admin WHERE email = ? AND password = ?',
            (email, hashed_password)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


# ✅ Save resume data
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


# ✅ Save AI analysis
def save_ai_analysis_data(resume_id, analysis_data):
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO ai_analysis (
            resume_id, model_used, resume_score, job_role
        ) VALUES (?, ?, ?, ?)
        """, (
            resume_id,
            analysis_data.get('model_used', ''),
            analysis_data.get('resume_score', 0),
            analysis_data.get('job_role', '')
        ))

        conn.commit()
        return cursor.lastrowid

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return None

    finally:
        conn.close()
