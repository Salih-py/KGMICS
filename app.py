import sqlite3
import json
import os
import re
import requests
from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from data.courses import COLLEGE_COURSES
from data.indian_jobs import INDIAN_JOB_POSTINGS
from services.kgimcs_engine import run_kgimcs_recommendation
from init_db import init_database

from services.resume_service import (
    RESUME_TEMPLATES, 
    build_default_resume_state, 
    process_bullet_improvement
)
# Load environment variables (for Groq API key if available)
load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_local_key_kgimcs_portal"

# Ensure all SQLite tables and columns exist on startup
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

    return render_template('dashboard/index.html', user=user, profile=profile, recs=None)

@app.route('/api/suggest_career', methods=['POST'])
def suggest_career():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    bio_text = data.get('bio_text', '').strip()

    if len(bio_text.split()) < 5:
        return jsonify({
            "status": "error", 
            "message": "Your bio is too short. Please provide at least a few sentences describing your skills, projects, or career goals so the AI can analyze your profile."
        })

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    engine_output = run_kgimcs_recommendation(
        registered_course_name=user['course_name'],
        bio_text=bio_text,
        interested_career=user['interested_career']
    )
    
    if engine_output.get("is_low_signal"):
        conn.close()
        return jsonify({
            "status": "error",
            "message": "We couldn't detect enough specific academic or technical skills in your bio. Please add specific tools, subjects, or laboratory techniques you know."
        })

    recommendations = engine_output['recommendations']
    metrics = engine_output['metrics']
    extracted_skills = engine_output['extracted_skills']
    novel_skills = engine_output.get('novel_skills', [])

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
        "novel_skills": novel_skills
    })

@app.route('/jobs')
def jobs_page():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    target_query = request.args.get('q', '').strip()
    selected_domain = request.args.get('domain', '').strip()

    filtered_jobs = []

    for job in INDIAN_JOB_POSTINGS:
        matches_query = True
        if target_query:
            query_lower = target_query.lower()
            text_pool = f"{job['title']} {job['company']} {' '.join(job['skills'])} {job['domain']}".lower()
            matches_query = query_lower in text_pool

        matches_domain = True
        if selected_domain:
            matches_domain = job['domain'] == selected_domain

        if matches_query and matches_domain:
            ncs_url = f"https://www.ncs.gov.in/job-listing?k={quote_plus(job['ncs_keyword'])}&l=India"
            job_copy = dict(job)
            job_copy['ncs_url'] = ncs_url
            filtered_jobs.append(job_copy)

    all_domains = sorted(list(set(j['domain'] for j in INDIAN_JOB_POSTINGS)))

    return render_template(
        'jobs/index.html',
        user=user,
        jobs=filtered_jobs,
        query=target_query,
        selected_domain=selected_domain,
        domains=all_domains,
        total_count=len(filtered_jobs)
    )

# ==========================================
# ATS RESUME BUILDER MODULE
# ==========================================

@app.route('/resume')
def resume_page():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    profile = conn.execute('SELECT * FROM student_profiles WHERE user_id = ?', (session['user_id'],)).fetchone()
    top_rec = conn.execute('SELECT career_title FROM career_recommendations WHERE user_id = ? ORDER BY match_score DESC LIMIT 1', (session['user_id'],)).fetchone()
    conn.close()

    nlp_skills = []
    if profile and profile['extracted_skills']:
        try:
            nlp_skills = json.loads(profile['extracted_skills'])
        except Exception:
            nlp_skills = []

    saved_resume = None
    if profile and 'resume_data' in profile.keys() and profile['resume_data']:
        try:
            saved_resume = json.loads(profile['resume_data'])
        except Exception:
            saved_resume = None

    if not saved_resume:
        saved_resume = build_default_resume_state(user, nlp_skills)

    target_career = top_rec['career_title'] if top_rec else (user['interested_career'] or 'Target Professional')

    return render_template(
        'resume/index.html',
        user=user,
        profile=profile,
        nlp_skills=nlp_skills,
        saved_resume=saved_resume,
        target_career=target_career,
        templates=RESUME_TEMPLATES
    )

@app.route('/api/resume/save', methods=['POST'])
def save_resume():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    resume_data = data.get('resume_data')

    if not resume_data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_profiles (user_id, resume_data)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET resume_data=excluded.resume_data
    ''', (session['user_id'], json.dumps(resume_data)))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Draft auto-saved successfully"})

@app.route('/api/resume/improve', methods=['POST'])
def improve_bullet():
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    section_title = data.get('section_title', 'Experience')
    entry_title = data.get('entry_title', 'General')
    target_role = data.get('target_role', '')

    if not text:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    improved_text, engine = process_bullet_improvement(text, section_title, entry_title, target_role)
    return jsonify({"status": "success", "improved_text": improved_text, "engine": engine})

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)