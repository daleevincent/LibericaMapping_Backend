from flask import Flask
from flask_cors import CORS
from .database.mongo import init_mongo
from .routes.prediction_routes import prediction_bp
from .routes.farm_routes import farm_bp
from app.database.mongo import init_mongo

def create_app():

    app = Flask(__name__)
    CORS(app)
    init_mongo(app)  # must be before routes are used

    app.register_blueprint(prediction_bp)
    app.register_blueprint(farm_bp)

    return app