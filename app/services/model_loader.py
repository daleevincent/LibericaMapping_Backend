from tensorflow.keras.models import load_model
import os

MODEL_PATHS = {
    "leaf": "models/leaf_MobileNetV2_80-20_model.keras",
    "bark": "models/bark_MobileNetV2_80-20_model.keras",
    "cherry": "models/cherry_MobileNetV2_80-20_model.keras"
}

MODELS = {}

def load_models():

    for organ, path in MODEL_PATHS.items():
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        MODELS[organ] = load_model(path)

    return MODELS