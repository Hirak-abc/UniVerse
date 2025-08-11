# personalised_feed.py
from flask import Blueprint, request, session, redirect, jsonify, Response
from bson.objectid import ObjectId
from db import mongo
import os
import datetime
import re

feed_blueprint = Blueprint(
    'feed',
    __name__,
    url_prefix='/feed'
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_html_response(filename):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def is_student(email):
    # Matches su-xxxxx@sitare.org
    return re.fullmatch(r"su-\d+@sitare\.org", email) is not None

def is_staff(email):
    # Matches any non-su prefix @sitare.org
    return re.fullmatch(r"[^@]+@sitare\.org", email) is not None and not is_student(email)

def allowed_file(filename, email):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()

    if is_staff(email):
        # Staff can upload images + videos
        return ext in ALLOWED_IMAGE_EXTENSIONS or ext in ALLOWED_VIDEO_EXTENSIONS
    elif is_student(email):
        # Students only images allowed
        return ext in ALLOWED_IMAGE_EXTENSIONS
    return False

@feed_blueprint.route('/', methods=['GET'])
def feed_home():
    if 'email' not in session:
        return redirect('/login')

    user_email = session['email']

    posts = list(mongo.db.feed.find().sort('created_at', -1))

    html_posts = ""
    for post in posts:
        content_html = f"<p>{post.get('text', '')}</p>"
        if post.get('file_type') == 'image':
            content_html += f"<img src='/static/uploads/{post['file_name']}' class='max-w-xs mt-2 rounded' />"
        elif post.get('file_type') == 'video':
            content_html += f"<video src='/static/uploads/{post['file_name']}' controls class='max-w-xs mt-2 rounded'></video>"

        # Likes count
        likes = post.get('likes', 0)
        post_id = str(post['_id'])

        html_posts += f"""
        <div class='bg-gray-800 p-4 rounded mt-4 relative' data-post-id="{post_id}">
            <strong>{post['author']}</strong> - <small>{post['created_at']}</small>
            {content_html}
            <div class="mt-2">
                <button onclick="likePost('{post_id}')" class="text-blue-400 hover:text-blue-600 font-semibold">
                    👍 Like (<span id="likes-count-{post_id}">{likes}</span>)
                </button>
            </div>
        </div>
        """

    base_html = load_html_response('feed.html')
    if base_html is None:
        return Response("<h2>feed.html not found in templates folder</h2>", mimetype='text/html')

    # Upload input control depends on role/email
    if is_staff(user_email):
        upload_section = """
        <input type="file" name="file" accept="image/*,video/*"
            class="w-full mb-4 p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-400" />
        """
    elif is_student(user_email):
        upload_section = """
        <input type="file" name="file" accept="image/*"
            class="w-full mb-4 p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-400" />
        """
    else:
        upload_section = "<p class='text-sm text-red-400 mb-4'>Upload not allowed for your email.</p>"

    base_html = base_html.replace("{{UPLOAD_SECTION}}", upload_section)
    base_html = base_html.replace("{{FEED_CONTENT}}", html_posts if html_posts else "<p>No posts yet.</p>")
    base_html = base_html.replace("{{USER_EMAIL}}", user_email)

    return Response(base_html, mimetype='text/html')


@feed_blueprint.route('/upload', methods=['POST'])
def upload_post():
    if 'email' not in session:
        return redirect('/login')

    user_email = session['email']
    text_content = request.form.get('text', '').strip()

    file = request.files.get('file')
    file_name = None
    file_type = None

    if file and file.filename != '':
        if not allowed_file(file.filename, user_email):
            return Response("<h2>File type not allowed for your email/role.</h2><a href='/feed'>Go Back</a>", mimetype='text/html')

        ext = file.filename.rsplit('.', 1)[1].lower()
        file_name = f"{ObjectId()}.{ext}"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        file.save(file_path)
        file_type = 'image' if ext in ALLOWED_IMAGE_EXTENSIONS else 'video'

    if not text_content and not file_name:
        return Response("<h2>Post must have text or media.</h2><a href='/feed'>Go Back</a>", mimetype='text/html')

    mongo.db.feed.insert_one({
        'author': user_email,
        'text': text_content,
        'file_name': file_name,
        'file_type': file_type,
        'likes': 0,
        'liked_by': [],          # Initialize liked_by list
        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return redirect('/feed')


@feed_blueprint.route('/myuploads', methods=['GET'])
def my_uploads_page():
    if 'email' not in session:
        return redirect('/login')

    user_email = session['email']
    posts = list(mongo.db.feed.find({'author': user_email}).sort('created_at', -1))

    html_posts = ""
    for post in posts:
        content_html = f"<p>{post.get('text', '')}</p>"
        if post.get('file_type') == 'image':
            content_html += f"<img src='/static/uploads/{post['file_name']}' class='max-w-xs mt-2 rounded' />"
        elif post.get('file_type') == 'video':
            content_html += f"<video src='/static/uploads/{post['file_name']}' controls class='max-w-xs mt-2 rounded'></video>"

        likes = post.get('likes', 0)
        post_id = str(post['_id'])

        html_posts += f"""
        <div class='bg-gray-800 p-4 rounded mt-4 relative' data-post-id="{post_id}">
            <strong>{post['author']}</strong> - <small>{post['created_at']}</small>
            {content_html}
            <div class="mt-2">
                <button onclick="likePost('{post_id}')" class="text-blue-400 hover:text-blue-600 font-semibold">
                    👍 Like (<span id="likes-count-{post_id}">{likes}</span>)
                </button>
            </div>
        </div>
        """

    base_html = load_html_response('my_uploads.html')
    if base_html is None:
        return Response("<h2>my_uploads.html not found in templates folder</h2>", mimetype='text/html')

    base_html = base_html.replace("{{FEED_CONTENT}}", html_posts if html_posts else "<p>You have no posts yet.</p>")
    base_html = base_html.replace("{{USER_EMAIL}}", user_email)

    return Response(base_html, mimetype='text/html')


@feed_blueprint.route('/like/<post_id>', methods=['POST'])
def like_post(post_id):
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_email = session['email']

    post = mongo.db.feed.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    liked_by = post.get('liked_by', [])
    if user_email in liked_by:
        return jsonify({'error': 'You have already liked this post.', 'likes': post.get('likes', 0)}), 400

    # Atomically update likes and liked_by
    result = mongo.db.feed.find_one_and_update(
        {'_id': ObjectId(post_id)},
        {'$inc': {'likes': 1}, '$push': {'liked_by': user_email}},
        return_document=True
    )

    return jsonify({'likes': result.get('likes', 0)})
