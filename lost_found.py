from flask import Blueprint, request, redirect, session, current_app, Response
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

        # File upload only if staff or top 50 student
        if file and (session['role'] == 'staff' or session['rank'] <= 50):
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            file.save(upload_path)
            filename = file.filename

        mongo.db.lost_found.insert_one({
            'email': session['email'],
            'message': message,
            'image': filename
        })
        return redirect('/lost_found')

    # Fetch items from database
    items = list(mongo.db.lost_found.find().sort('_id', -1))

    # Build HTML manually
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Lost & Found</title></head>
    <body>
        <h1>Lost & Found</h1>
        <form method="POST" enctype="multipart/form-data">
            <textarea name="message" placeholder="Describe the item..." required></textarea><br>
            <input type="file" name="file"><br>
            <button type="submit">Submit</button>
        </form>
        <hr>
        <h2>Submitted Items:</h2>
    """

    for item in items:
        html += f"<p><strong>{item['email']}</strong>: {item['message']}<br>"
        if item.get('image'):
            image_url = f"/static/uploads/{item['image'].split('/')[-1]}"
            html += f"<img src='{image_url}' width='200'><br>"
        html += "</p><hr>"

    html += "</body></html>"

    return Response(html, mimetype='text/html')
