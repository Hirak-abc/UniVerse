from flask import Flask, request, redirect, session, url_for, flash, Response
from datetime import timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import Blueprints
from auth import auth_blueprint
from lost_found import lost_found_blueprint
from features.events_clubs import events_clubs_blueprint  
from features.ai_study_assistant import chatbot_blueprint
from features.marketplace import marketplace_blueprint
from features.academic_corner import get_academic_corner_page
from features.news import news_blueprint
from features.settings import settings_bp  
from features.personalized_feed import feed_blueprint 

# Import Mongo connection setup
from db import init_app as init_db, mongo

app = Flask(__name__)

# Flask session config
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize MongoDB connection
init_db(app)

# Blueprint Registration
app.register_blueprint(chatbot_blueprint, url_prefix="/study_assistant") 
app.register_blueprint(auth_blueprint)
app.register_blueprint(lost_found_blueprint)
app.register_blueprint(events_clubs_blueprint)
app.register_blueprint(marketplace_blueprint, url_prefix="/marketplace")
app.register_blueprint(news_blueprint, url_prefix="/news")
app.register_blueprint(settings_bp, url_prefix="/settings")  
app.register_blueprint(feed_blueprint)  # ✅ REGISTER FEED (prefix already inside blueprint)

# Manual HTML Loader
def load_html(filename):
    filepath = os.path.join(app.root_path, 'templates', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# Home Page
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

# Academic Corner
@app.route('/academic')
def academic_corner():
    html_content = get_academic_corner_page()
    return Response(html_content, mimetype='text/html')

# Start Flask App
if __name__ == '__main__':
    app.run(debug=True)
