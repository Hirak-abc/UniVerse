from flask import Blueprint, render_template, request, redirect, session, current_app
from db import mongo
import os

lost_found_blueprint = Blueprint('lost_found', __name__)

@lost_found_blueprint.route('/lost_found', methods=['GET', 'POST'])
def lost_found():
    if 'email' not in session:
        return redirect('/login')
    if request.method == 'POST':
        message = request.form['message']
        file = request.files.get('file')
        filename = None
        if file and (session['role'] == 'staff' or session['rank'] <= 50):
            filename = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
        mongo.db.lost_found.insert_one({
            'email': session['email'],
            'message': message,
            'image': filename
        })
        return redirect('/lost_found')
    items = list(mongo.db.lost_found.find().sort('_id', -1))
    return render_template('lost_found.html', items=items)
