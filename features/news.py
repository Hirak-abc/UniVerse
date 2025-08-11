from flask import Blueprint, request, redirect, url_for, session, flash, Response
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from db import mongo

news_blueprint = Blueprint('news', __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'news')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@news_blueprint.route('/', methods=['GET'])
def news():
    if 'email' not in session:
        flash("Please log in to view news.")
        return redirect(url_for('auth.login'))

    news_collection = mongo.db.news
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    news_collection.delete_many({"created_at": {"$lt": thirty_days_ago}})

    news_items = list(news_collection.find().sort('_id', -1))

    with open('templates/news.html', 'r', encoding='utf-8') as f:
        html = f.read()

    news_html = ""
    for item in news_items:
        media_html = ""
        if item.get('media_filename'):
            ext = item['media_filename'].rsplit('.', 1)[1].lower()
            if ext in ['mp4', 'webm', 'ogg']:
                media_html = f"""
                <video controls class="rounded-lg w-full max-w-lg mx-auto mt-3">
                    <source src="/static/uploads/news/{item['media_filename']}" type="video/{ext}">
                </video>
                """
            else:
                media_html = f"""
                <img src="/static/uploads/news/{item['media_filename']}" 
                     class="rounded-lg w-full max-w-lg mx-auto mt-3" alt="news media"/>
                """

        news_html += f"""
        <div class="bg-gray-800 rounded-lg shadow-lg p-6 text-center">
            <h2 class="text-2xl font-bold text-blue-400 mb-2">{item['title']}</h2>
            <p class="text-gray-400 text-sm mb-4">{item['description']}</p>
            {media_html}
            <p class="text-xs text-gray-500 mt-4">Posted by: {item['email']}</p>
        </div>
        """

    html = html.replace("{{ news_items }}", news_html)
    return Response(html, mimetype='text/html')

@news_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_news():
    if 'email' not in session:
        flash("Please log in to post news.")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        media = request.files.get('media', None)

        media_filename = ''
        if media and allowed_file(media.filename):
            filename = secure_filename(media.filename)
            media.save(os.path.join(UPLOAD_FOLDER, filename))
            media_filename = filename

        news_item = {
            'title': title,
            'description': description,
            'media_filename': media_filename,
            'email': session['email'],
            'created_at': datetime.utcnow()
        }
        mongo.db.news.insert_one(news_item)
        flash("News item uploaded successfully!")
        return redirect(url_for('news.news'))

    with open('templates/news_upload.html', 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')
