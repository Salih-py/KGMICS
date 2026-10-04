import sqlite3

def init_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            course_category TEXT,
            course_name TEXT NOT NULL,
            passout_year INTEGER,
            interested_career TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Student Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            bio_text TEXT,
            extracted_skills TEXT,
            resume_data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 3. Career Recommendations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            career_title TEXT NOT NULL,
            match_score REAL NOT NULL,
            reasoning_path TEXT,
            missing_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Safe Migration: Ensure resume_data column exists if database was created previously
    try:
        cursor.execute("ALTER TABLE student_profiles ADD COLUMN resume_data TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    print("Database verified and schema migrated successfully.")