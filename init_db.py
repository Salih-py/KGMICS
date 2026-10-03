import sqlite3

def init_database(db_path='database.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            course_category TEXT NOT NULL,
            course_name TEXT NOT NULL,
            passout_year INTEGER NOT NULL,
            interested_career TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Student profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            user_id INTEGER PRIMARY KEY,
            bio_text TEXT,
            extracted_skills TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Career recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            career_title TEXT NOT NULL,
            match_score REAL NOT NULL,
            reasoning_path TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    print("Database tables verified and created successfully.")