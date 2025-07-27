from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from db import mongo

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
            session['rank'] = user['rank']
            return redirect(url_for('home'))
        return 'Invalid credentials'
    return render_template('login.html')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        role = 'staff' if '@sitare.org' in email and not email.startswith('su-') else 'student'
        rank = 51  # default rank
        mongo.db.users.insert_one({'email': email, 'password': hashed_pw, 'role': role, 'rank': rank})
        return redirect(url_for('auth.login'))
    return render_template('register.html')
