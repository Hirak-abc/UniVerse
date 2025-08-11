from flask import Blueprint, request, redirect, session, url_for, Response, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from db import mongo  # ✅ uses the shared mongo instance initialized in app.py
import requests
import os

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['email'] = user['email']
            session['role'] = user['role']
            session['rank'] = user.get('rank', '')

            if user['role'] == 'student' and 'leetcode_id' not in user:
                return redirect('/update_leetcode')

            return redirect(url_for('home'))

        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login'))

    return load_html_response('login.html')


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password)
        role = 'staff' if '@sitare.org' in email and not email.startswith('su-') else 'student'

        user_doc = {
            'email': email,
            'password': hashed_pw,
            'role': role
        }

        if role == 'staff':
            user_doc['rank'] = 0

        mongo.db.users.insert_one(user_doc)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return load_html_response('register.html')


@auth_blueprint.route('/update_leetcode', methods=['GET', 'POST'])
def update_leetcode():
    if 'email' not in session or session.get('role') != 'student':
        return redirect('/login')

    if request.method == 'POST':
        leetcode_id = request.form['leetcode_id'].strip()
        leetcode_rank = get_leetcode_rank(leetcode_id)

        if leetcode_rank is None:
            return Response(f"""
                <h2>Invalid or unavailable LeetCode ID</h2>
                <p>Make sure the username exists: 
                    <a href='https://leetcode.com/u/{leetcode_id}/' target='_blank'>Check Profile</a>
                </p>
                <a href='/update_leetcode'>Try Again</a>
            """, mimetype='text/html')

        mongo.db.users.update_one(
            {'email': session['email']},
            {'$set': {
                'leetcode_id': leetcode_id,
                'leetcode_rank': leetcode_rank
            }}
        )

        recalculate_platform_ranks()
        user = mongo.db.users.find_one({'email': session['email']})
        session['rank'] = user['rank']

        return redirect('/')

    return load_html_response('leetcode.html')


def get_leetcode_rank(username):
    try:
        url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Error fetching rank: Status {res.status_code}")
            return None
        data = res.json()
        ranking = data.get('ranking')
        if ranking is None:
            print(f"Ranking not found in response: {data}")
        return ranking
    except Exception as e:
        print(f"Exception during LeetCode rank fetch: {e}")
        return None


def recalculate_platform_ranks():
    students = list(mongo.db.users.find({
        'role': 'student',
        'leetcode_rank': {'$exists': True}
    }))
    sorted_students = sorted(students, key=lambda x: x['leetcode_rank'])
    for idx, student in enumerate(sorted_students, start=1):
        mongo.db.users.update_one({'_id': student['_id']}, {'$set': {'rank': idx}})


def load_html_response(filename):
    base_path = os.path.join(os.path.dirname(__file__), 'templates')
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        return 'Template not found', 404
    with open(filepath, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')
