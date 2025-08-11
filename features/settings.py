from flask import Blueprint, session, redirect, url_for, request, Response
from werkzeug.utils import secure_filename
from db import mongo
import os

settings_bp = Blueprint('settings', __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profile_pics')
ALLOWED_IMG_EXT = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'templates', 'settings.html')

def _get_logged_in_email():
    return session.get('email') or session.get('username')

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXT


@settings_bp.route('/', methods=['GET'])
@settings_bp.route('/settings', methods=['GET'])
def settings_page():
    email = _get_logged_in_email()
    if not email:
        return redirect(url_for('auth.login'))

    user = mongo.db.users.find_one({'email': email}) or {}

    leetcode_id = user.get('leetcode_id', '')
    profile_pic = user.get('profile_pic')
    profile_pic_url = ''
    if profile_pic:
        profile_pic_url = url_for('static', filename=f'uploads/profile_pics/{profile_pic}')

    msg = request.args.get('msg', '')

    with open(TEMPLATE_PATH, encoding='utf-8') as f:
        html_template = f.read()

    # Build profile pic section with hover edit button
    if profile_pic_url:
        profile_pic_section = f"""
        <div class='relative group w-28 h-28'>
            <img src='{profile_pic_url}' class='w-28 h-28 object-cover rounded-full border' alt='Profile Pic'/>
            <div class='absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition'>
                <button onclick="document.getElementById('changePicInput').click()" class='text-white px-2 py-1 bg-indigo-600 rounded mr-1'>✏ Edit</button>
                <form action='/settings/delete_photo' method='POST' style='display:inline;'>
                    <button type='submit' class='text-white px-2 py-1 bg-red-500 rounded'>🗑 Delete</button>
                </form>
            </div>
        </div>
        """
    else:
        profile_pic_section = f"""
        <div class='relative group w-28 h-28 rounded-full bg-gray-200 flex items-center justify-center text-gray-500'>
            No Pic
            <div class='absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition'>
                <button onclick="document.getElementById('changePicInput').click()" class='text-white px-2 py-1 bg-indigo-600 rounded'>+ Add</button>
            </div>
        </div>
        """

    msg_section = f"<div class='mb-4 text-sm text-green-600'>{msg}</div>" if msg else ""

    html_filled = (
        html_template
        .replace("{{email}}", email)
        .replace("{{leetcode_id}}", leetcode_id or "")
        .replace("{{msg_section}}", msg_section)
        .replace("{{profile_pic_section}}", profile_pic_section)
    )

    return Response(html_filled, mimetype='text/html')


@settings_bp.route('/update_profile', methods=['POST'])
def update_profile():
    email = _get_logged_in_email()
    if not email:
        return redirect(url_for('auth.login'))

    updates = {}
    leetcode_id = request.form.get('leetcode_id', '').strip()
    if leetcode_id:
        updates['leetcode_id'] = leetcode_id

    file = request.files.get('profile_pic')
    if file and file.filename and _allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            counter += 1

        file.save(save_path)
        updates['profile_pic'] = filename

    if updates:
        mongo.db.users.update_one({'email': email}, {'$set': updates}, upsert=False)

    return redirect(url_for('settings.settings_page', msg='Profile updated successfully'))


@settings_bp.route('/delete_photo', methods=['POST'])
def delete_photo():
    email = _get_logged_in_email()
    if not email:
        return redirect(url_for('auth.login'))

    mongo.db.users.update_one({'email': email}, {'$unset': {'profile_pic': ""}})
    return redirect(url_for('settings.settings_page', msg='Profile picture removed successfully'))


@settings_bp.route('/logout', methods=['GET'])
@settings_bp.route('/settings/logout', methods=['GET'])
def logout():
    for k in ('email', 'username', 'role', 'rank'):
        session.pop(k, None)
    return redirect(url_for('auth.login'))
