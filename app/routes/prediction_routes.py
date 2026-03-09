from flask import Blueprint, request, jsonify
from app.services.prediction_services import predict_image

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/predict", methods=["POST"])
def predict():

    file = request.files["file"]
    plant_part = request.form.get("plant_part", "mix")

    result = predict_image(file.read(), plant_part)

    return jsonify(result)