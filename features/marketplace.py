from flask import Blueprint, request, redirect, session, current_app, url_for, flash
from db import mongo
import os
from werkzeug.utils import secure_filename

marketplace_blueprint = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_blueprint.route('/', methods=['GET', 'POST'])
def marketplace():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']
        description = request.form['description']
        file = request.files.get('file')
        filename = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

        mongo.db.marketplace.insert_one({
            'email': session['email'],
            'product_name': product_name,
            'price': price,
            'description': description,
            'image': filename
        })

        flash("Product listed successfully!")
        return redirect(url_for('marketplace.marketplace'))

    items = list(mongo.db.marketplace.find().sort('_id', -1))

    for item in items:
        if item.get('image'):
            item['image_url'] = url_for('static', filename=f'uploads/{item["image"]}')
        else:
            item['image_url'] = None

    # Read the template manually
    with open(os.path.join(current_app.root_path, 'templates', 'marketplace.html'), 'r') as file:
        html_template = file.read()

    item_cards = ''
    for item in items:
        card = f'''
        <div class="p-4 border rounded mb-4">
            <h2 class="text-xl font-bold">{item.get('product_name')}</h2>
            <p class="text-gray-700 mb-1"><strong>Price:</strong> ₹{item.get('price')}</p>
            <p class="mb-2">{item.get('description')}</p>
            {"<img src='" + item["image_url"] + "' class='w-48 h-48 object-cover'/>" if item["image_url"] else ""}
        </div>
        '''
        item_cards += card

    return html_template.replace("{{ item_cards }}", item_cards)

