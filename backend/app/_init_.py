from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    mongo.init_app(app)

    with app.app_context():
        from app.routes import init_routes
        init_routes(app)

    return app
