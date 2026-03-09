from flask import request, jsonify, Blueprint
from app.services.prediction_services import predict_image
from app.models.farm_model import FarmModel

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/predict", methods=["POST"])
def predict():

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    plant_part = request.form.get("plant_part", "mix")

    # Optional coordinates
    lat = request.form.get("lat", type=float)
    lng = request.form.get("lng", type=float)

    # Run your ML prediction
    result = predict_image(file.read(), plant_part)

    # Save prediction + coordinates if provided
    if lat is not None and lng is not None:
        farm_data = {
            "coordinates": {"lat": lat, "lng": lng},
            "prediction": result["final_prediction"],
            "confidence_ratio": result["confidence_ratio"],
            "plant_part_mode": result["plant_part_mode"]
        }
        FarmModel.create(farm_data)

    return jsonify(result)