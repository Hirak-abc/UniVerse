from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import timedelta
from db import mongo  # <-- import from db.py
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/universe_platform'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

mongo.init_app(app)  # <-- initialize here

from auth import auth_blueprint
from lost_found import lost_found_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(lost_found_blueprint)

@app.route('/')
def home():
    if 'email' in session:
        return render_template('index.html', user=session['email'], role=session['role'], rank=session['rank'])
    return render_template('login.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
