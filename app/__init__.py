from flask import Flask
from flask_cors import CORS
from .database.mongo import init_mongo
from .routes.prediction_routes import prediction_bp
from .routes.farm_routes import farm_bp
from .routes.tree_routes import tree_bp
from .routes.directions_routes import directions_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_mongo(app)

    app.register_blueprint(prediction_bp)
    app.register_blueprint(farm_bp)
    app.register_blueprint(tree_bp)
    app.register_blueprint(directions_bp)

    return app