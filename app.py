import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from data.courses import COLLEGE_COURSES
from services.kgimcs_engine import run_kgimcs_recommendation
from init_db import init_database

app = Flask(__name__)
app.secret_key = "super_secret_local_key_kgimcs_portal"

# Ensure all SQLite tables exist on startup
init_database()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing/index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        gender = request.form.get('gender', '')
        age = request.form.get('age', '')
        course_name = request.form.get('course_name', '')
        passout_year = request.form.get('passout_year', '')
        interested_career = request.form.get('interested_career', '').strip()

        if not full_name or not email or not password or not course_name:
            flash("All mandatory fields must be filled.", "error")
            return render_template('auth/signup.html', courses=COLLEGE_COURSES)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('auth/signup.html', courses=COLLEGE_COURSES)

        course_category = "UG"
        for category, list_of_courses in COLLEGE_COURSES.items():
            if course_name in list_of_courses:
                course_category = category
                break

        conn = get_db_connection()
        cursor = conn.cursor()

        existing_user = cursor.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            conn.close()
            flash("Email is already registered. Please sign in.", "error")
            return redirect(url_for('signin'))

        pw_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (full_name, email, password_hash, gender, age, course_category, course_name, passout_year, interested_career)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            full_name,
            email,
            pw_hash,
            gender,
            int(age) if age.isdigit() else 20,
            course_category,
            course_name,
            int(passout_year) if passout_year.isdigit() else 2026,
            interested_career
        ))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        session['user_id'] = user_id
        session['user_name'] = full_name
        session['course_name'] = course_name
        flash("Registration successful! Welcome to the portal.", "success")
        return redirect(url_for('dashboard'))

    return render_template('auth/signup.html', courses=COLLEGE_COURSES)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['course_name'] = user['course_name']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")

    return render_template('auth/signin.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    profile = conn.execute('SELECT * FROM student_profiles WHERE user_id = ?', (session['user_id'],)).fetchone()
    conn.close()

    # Pass recs=None so the initial dashboard view is clean
    return render_template('dashboard/index.html', user=user, profile=profile, recs=None)

@app.route('/api/suggest_career', methods=['POST'])
def suggest_career():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    bio_text = data.get('bio_text', '').strip()

    # Reject completely empty or meaningless bios before processing
    if len(bio_text.split()) < 5:
        return jsonify({
            "status": "error", 
            "message": "Your bio is too short. Please provide at least a few sentences describing your skills, projects, or career goals so the AI can analyze your profile."
        })

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    # Run the KGIMCS Recommender Engine
    engine_output = run_kgimcs_recommendation(
        registered_course_name=user['course_name'],
        bio_text=bio_text,
        interested_career=user['interested_career']
    )
    
    # If the NLP engine found the text too messy/unrelated to academic skills
    if engine_output.get("is_low_signal"):
        conn.close()
        return jsonify({
            "status": "error",
            "message": "We couldn't detect enough specific academic or technical skills in your bio. Please add specific tools, subjects, or laboratory techniques you know."
        })

    recommendations = engine_output['recommendations']
    metrics = engine_output['metrics']
    extracted_skills = engine_output['extracted_skills']
    novel_skills = engine_output.get('novel_skills', []) # NEW: Get out-of-mapping skills

    # Persist BOTH extracted and novel skills to SQLite
    cursor = conn.cursor()
    combined_skills = extracted_skills + novel_skills
    cursor.execute('''
        INSERT INTO student_profiles (user_id, bio_text, extracted_skills)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET bio_text=excluded.bio_text, extracted_skills=excluded.extracted_skills
    ''', (user['id'], bio_text, json.dumps(combined_skills)))

    cursor.execute('DELETE FROM career_recommendations WHERE user_id = ?', (user['id'],))
    for rec in recommendations:
        cursor.execute('''
            INSERT INTO career_recommendations (user_id, career_title, match_score, reasoning_path, missing_skills)
            VALUES (?, ?, ?, ?, ?)
        ''', (user['id'], rec['career_title'], rec['match_score'], rec['reasoning_path'], json.dumps(rec['missing_skills'])))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "recommendations": recommendations,
        "metrics": metrics,
        "extracted_skills": extracted_skills,
        "novel_skills": novel_skills # Send to JS
    })

@app.route('/jobs')
def jobs_page():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    target_query = request.args.get('q', '').strip()
    return render_template('jobs/index.html', query=target_query)

@app.route('/resume')
def resume_page():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    profile = conn.execute('SELECT * FROM student_profiles WHERE user_id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('resume/index.html', user=user, profile=profile)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)