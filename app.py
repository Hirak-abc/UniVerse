from flask import Flask, request, redirect, session, url_for, flash, Response
from datetime import timedelta
from db import mongo
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from auth import auth_blueprint
from lost_found import lost_found_blueprint

app = Flask(__name__)

# Secret key for session encryption
app.secret_key = os.environ['FLASK_SECRET_KEY']

# MongoDB configuration
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/universe_platform')

# Session settings
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Initialize MongoDB with Flask app
mongo.init_app(app)

# Register modular Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(lost_found_blueprint)

def load_html(filename):
    """Helper to load static HTML files from templates/ folder."""
    filepath = os.path.join(app.root_path, 'templates', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/')
def home():
    if 'email' in session:
        users_collection = mongo.db.users
        user = users_collection.find_one({'email': session['email']})
        
        if not user:
            flash("User not found. Please log in again.")
            return redirect(url_for('auth.login'))

        html = load_html('index.html')
        html = html.replace('{{ user }}', user.get('email', 'Unknown'))
        html = html.replace('{{ role }}', user.get('role', 'N/A'))
        html = html.replace('{{ rank }}', str(user.get('rank', 'N/A')))
        return Response(html, mimetype='text/html')
    
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
