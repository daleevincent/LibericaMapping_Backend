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

@farm_bp.route("/<int:farm_id>", methods=["GET"])
def get_farm(farm_id):
    farm = FarmModel.get_by_id(farm_id)
    if not farm:
        return jsonify({"error": "Farm not found"}), 404
    farm["_id"] = str(farm["_id"])
    return jsonify(farm)

@farm_bp.route("/<int:farm_id>", methods=["PUT"])
def update_farm(farm_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    data.pop("_id", None)  # remove _id from payload
    count = FarmModel.update(farm_id, data)
    if count == 0:
        return jsonify({"error": "Farm not found or no changes"}), 404
    farm = FarmModel.get_by_id(farm_id)
    farm["_id"] = str(farm["_id"])
    return jsonify(farm)