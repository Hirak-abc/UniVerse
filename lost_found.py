from flask import Blueprint, request, redirect, session, current_app, render_template, url_for, flash
from db import mongo
import os
from werkzeug.utils import secure_filename

lost_found_blueprint = Blueprint('lost_found', __name__, url_prefix='/lost_found')

@lost_found_blueprint.route('/', methods=['GET', 'POST'])
def lost_found():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        message = request.form['message']
        file = request.files.get('file')
        filename = None

        # If a file is uploaded, save it
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

        # Save to MongoDB
        mongo.db.lost_found.insert_one({
            'email': session['email'],
            'message': message,
            'image': filename
        })

        flash("Item submitted successfully!")
        return redirect(url_for('lost_found.lost_found'))

    # Fetch all lost & found items
    items = list(mongo.db.lost_found.find().sort('_id', -1))

    # Add image URL for display
    for item in items:
        if item.get('image'):
            item['image_url'] = url_for('static', filename=f'uploads/{item["image"]}')
        else:
            item['image_url'] = None

    return render_template('lost_found.html', items=items)
