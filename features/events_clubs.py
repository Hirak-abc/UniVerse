from flask import Blueprint, request, session, redirect, url_for, flash, Response
from bson import ObjectId
from db import mongo
import datetime
import os
from werkzeug.utils import secure_filename

events_clubs_blueprint = Blueprint('events_clubs', __name__, url_prefix='/events')

# ====== Photo Upload Config ======
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# =================================

def get_gradient_color(progress):
    if progress <= 0:
        return "rgb(0,255,0)"
    elif progress >= 1:
        return "rgb(255,0,0)"
    elif progress <= 0.5:
        ratio = progress / 0.5
        r = int(255 * ratio)
        g = 255
    else:
        ratio = (progress - 0.5) / 0.5
        r = 255
        g = int(255 * (1 - ratio))
    return f"rgb({r},{g},0)"

def load_html(filename):
    filepath = os.path.join(os.path.dirname(__file__), '..', 'templates', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

@events_clubs_blueprint.route('/')
def view_events():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    events = list(mongo.db.events.find().sort('date', 1))
    user_email = session['email']
    today = datetime.date.today()
    processed_events = []

    for e in events:
        event_date_str = e.get('date', '')
        created_at = e.get('created_at')

        try:
            event_date = datetime.datetime.strptime(event_date_str, "%Y-%m-%d").date()

            if event_date < today:
                mongo.db.events.delete_one({'_id': e['_id']})
                continue

            start_date = created_at.date() if isinstance(created_at, datetime.datetime) else today
            total_days = (event_date - start_date).days
            elapsed_days = (today - start_date).days

            progress = 1.0 if total_days <= 0 else max(0, min(1, elapsed_days / total_days))
            pointer_percent = progress * 100
            pointer_color = get_gradient_color(progress)

            days_left = (event_date - today).days
        except Exception:
            pointer_percent = 0
            pointer_color = "black"
            days_left = 'N/A'

        processed_events.append({
            '_id': str(e['_id']),
            'title': e.get('title', 'Untitled'),
            'date': event_date_str,
            'description': e.get('description', ''),
            'photo': e.get('photo', None),
            'created_by': e.get('created_by', 'Unknown'),
            'pointer_percent': pointer_percent,
            'pointer_color': pointer_color,
            'days_left': days_left
        })

    base_html = load_html('events.html')

    if processed_events:
        event_blocks = ""
        for event in processed_events:
            delete_button = ""
            if event['created_by'] == user_email:
                delete_button = f"""
                    <form method="POST" action="/events/delete/{event['_id']}" class="mt-3">
                        <button class="text-red-600 hover:underline">Delete</button>
                    </form>
                """

            photo_html = f'<img src="{event["photo"]}" alt="{event["title"]}" class="mt-2 rounded max-h-48 object-cover">' if event['photo'] else ""

            event_html = f"""
                <div class="border border-gray-700 rounded-lg p-4 mb-6 bg-gray-800">
                    <h3 class="text-lg font-semibold text-indigo-400">{event['title']} ({event['date']})</h3>
                    {photo_html}
                    <div class="color-bar mt-2">
                        <div class="pointer" style="left: {event['pointer_percent']}%; border-bottom-color: {event['pointer_color']}"></div>
                    </div>
                    <p class="text-gray-300">{event['description']}</p>
                    <p class="text-sm mt-2 text-gray-400"><strong>Days left:</strong> {event['days_left']}</p>
                    <p class="text-sm text-gray-400"><strong>Announced by:</strong> {event['created_by']}</p>
                    {delete_button}
                </div>
            """
            event_blocks += event_html
    else:
        event_blocks = '<p class="text-gray-400">No events found.</p>'

    html_output = base_html.replace('{{ user_email }}', user_email)
    html_output = html_output.replace('<!--DYNAMIC_EVENTS-->', event_blocks)

    return Response(html_output, mimetype='text/html')

@events_clubs_blueprint.route('/add')
def add_event_page():
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    html = load_html('add_event.html')
    return Response(html, mimetype='text/html')

@events_clubs_blueprint.route('/create', methods=['POST'])
def create_event():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    title = request.form.get('title')
    date = request.form.get('date')
    description = request.form.get('description')

    # Handle photo upload
    photo_path = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            photo_path = f"/static/uploads/{filename}"

    mongo.db.events.insert_one({
        'title': title,
        'date': date,
        'description': description,
        'photo': photo_path,
        'created_by': session['email'],
        'created_at': datetime.datetime.utcnow()
    })

    flash("Event created successfully.")
    return redirect(url_for('events_clubs.view_events'))

@events_clubs_blueprint.route('/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    event = mongo.db.events.find_one({'_id': ObjectId(event_id)})
    if not event:
        flash("Event not found.")
        return redirect(url_for('events_clubs.view_events'))

    if event['created_by'] != session['email']:
        flash("Unauthorized to delete this event.")
        return redirect(url_for('events_clubs.view_events'))

    mongo.db.events.delete_one({'_id': ObjectId(event_id)})
    flash("Event deleted.")
    return redirect(url_for('events_clubs.view_events'))
