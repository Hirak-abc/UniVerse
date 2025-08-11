# db.py
import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()  # Load .env file

mongo = PyMongo()

def init_app(app):
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo.init_app(app)
