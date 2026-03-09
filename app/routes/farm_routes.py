from flask import Blueprint, request, jsonify
from app.models.farm_model import FarmModel

farm_bp = Blueprint("farms", __name__, url_prefix="/farms")

@farm_bp.route("/", methods=["POST"])
def create_farm():

    data = request.json
    FarmModel.create(data)

    return jsonify({"message": "Farm created"})


@farm_bp.route("/", methods=["GET"])
def get_farms():

    farms = FarmModel.get_all()

    for farm in farms:
        farm["_id"] = str(farm["_id"])

    return jsonify(farms)