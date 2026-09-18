import tensorflow as tf
from keras.models import Model
import numpy as np
import cv2
from app.utils.image_utils import preprocess_pil_image, image_to_base64
from app.services.model_loader import load_models

MODELS = load_models()

# ── OOD rejection constants ───────────────────────────────────────────────────
MIN_CONFIDENCE  = 0.80   # must be at least 80% confident
MAX_UNCERTAINTY = 0.35   # reject if too uncertain

def get_uncertainty(liberica_prob):
    """Entropy-based uncertainty. 0 = certain, 1 = completely uncertain."""
    p = liberica_prob
    q = 1 - p
    entropy = -(p * np.log(p + 1e-9) + q * np.log(q + 1e-9))
    return entropy / np.log(2)

def classify_single_model(pred_prob, threshold=0.50):
    """
    Apply threshold + confidence + uncertainty filter to a single model output.
    Returns predicted_class, confidence, uncertainty.
    """
    liberica_prob = float(pred_prob)
    not_lib_prob  = 1.0 - liberica_prob
    confidence    = max(liberica_prob, not_lib_prob)
    uncertainty   = get_uncertainty(liberica_prob)

    if uncertainty > MAX_UNCERTAINTY or confidence < MIN_CONFIDENCE:
        predicted_class = "Unknown"
    elif liberica_prob >= threshold:
        predicted_class = "Liberica"
    else:
        predicted_class = "Not Liberica"

    return predicted_class, round(confidence * 100, 2), round(uncertainty * 100, 2), round(liberica_prob * 100, 2)


# =========================
# Individual model predictors
# =========================

def predict_leaf(file_bytes):
    """Predict using leaf model only."""
    arr, original_img = preprocess_pil_image(file_bytes)
    model = MODELS['leaf']

    pred          = model.predict(arr, verbose=0)
    label, conf, uncert, lib_prob = classify_single_model(pred[0][0])

    heatmap = make_gradcam_heatmap(arr, model)
    gradcam_image = None
    if heatmap is not None:
        superimposed = create_superimposed_gradcam(original_img, heatmap)
        gradcam_image = image_to_base64(superimposed)

    return {
        "final_prediction" : label,
        "plant_part_mode"  : "leaf",
        "confidence_ratio" : conf,
        "uncertainty"      : uncert,
        "liberica_prob"    : lib_prob,
        "gradcam_image"    : gradcam_image,
        "individual_predictions": {
            "leaf": {
                "prediction"   : label,
                "confidence"   : conf,
                "liberica_prob": lib_prob,
                "uncertainty"  : uncert,
            }
        }
    }


def predict_bark(file_bytes):
    """Predict using bark model only."""
    arr, original_img = preprocess_pil_image(file_bytes)
    model = MODELS['bark']

    pred          = model.predict(arr, verbose=0)
    label, conf, uncert, lib_prob = classify_single_model(pred[0][0])

    heatmap = make_gradcam_heatmap(arr, model)
    gradcam_image = None
    if heatmap is not None:
        superimposed = create_superimposed_gradcam(original_img, heatmap)
        gradcam_image = image_to_base64(superimposed)

    return {
        "final_prediction" : label,
        "plant_part_mode"  : "bark",
        "confidence_ratio" : conf,
        "uncertainty"      : uncert,
        "liberica_prob"    : lib_prob,
        "gradcam_image"    : gradcam_image,
        "individual_predictions": {
            "bark": {
                "prediction"   : label,
                "confidence"   : conf,
                "liberica_prob": lib_prob,
                "uncertainty"  : uncert,
            }
        }
    }


def predict_cherry(file_bytes):
    """Predict using cherry model only."""
    arr, original_img = preprocess_pil_image(file_bytes)
    model = MODELS['cherry']

    pred          = model.predict(arr, verbose=0)
    label, conf, uncert, lib_prob = classify_single_model(pred[0][0])

    heatmap = make_gradcam_heatmap(arr, model)
    gradcam_image = None
    if heatmap is not None:
        superimposed = create_superimposed_gradcam(original_img, heatmap)
        gradcam_image = image_to_base64(superimposed)

    return {
        "final_prediction" : label,
        "plant_part_mode"  : "cherry",
        "confidence_ratio" : conf,
        "uncertainty"      : uncert,
        "liberica_prob"    : lib_prob,
        "gradcam_image"    : gradcam_image,
        "individual_predictions": {
            "cherry": {
                "prediction"   : label,
                "confidence"   : conf,
                "liberica_prob": lib_prob,
                "uncertainty"  : uncert,
            }
        }
    }


def predict_mix(file_bytes):
    """Predict using all 3 models — majority vote with OOD rejection."""
    arr, original_img = preprocess_pil_image(file_bytes)

    liberica_votes     = 0
    not_lib_votes      = 0
    unknown_votes      = 0
    max_confidence     = 0
    winning_model      = None
    winning_organ      = None
    individual_predictions = {}

    for organ, model in MODELS.items():
        pred                         = model.predict(arr, verbose=0)
        label, conf, uncert, lib_prob = classify_single_model(pred[0][0])

        individual_predictions[organ] = {
            "prediction"   : label,
            "confidence"   : conf,
            "liberica_prob": lib_prob,
            "uncertainty"  : uncert,
        }

        if label == "Liberica":
            liberica_votes += 1
        elif label == "Not Liberica":
            not_lib_votes += 1
        else:
            unknown_votes += 1

        if conf / 100 > max_confidence:
            max_confidence = conf / 100
            winning_model  = model
            winning_organ  = organ

    # ── Final decision ────────────────────────────────────────────────────────
    total_definitive = liberica_votes + not_lib_votes

    if unknown_votes == 3:
        # All 3 models rejected it — definitely not a coffee plant
        final_prediction = "Unknown"
        confidence_ratio = 0.0
    elif total_definitive == 0:
        final_prediction = "Unknown"
        confidence_ratio = 0.0
    elif liberica_votes >= 2:
        final_prediction = "Liberica"
        confidence_ratio = round(liberica_votes / 3 * 100, 2)
    elif not_lib_votes >= 2:
        final_prediction = "Not Liberica"
        confidence_ratio = round(not_lib_votes / 3 * 100, 2)
    else:
        # 1 Liberica, 1 Not Liberica, 1 Unknown — inconclusive
        final_prediction = "Unknown"
        confidence_ratio = 0.0

    # ── Grad-CAM from winning model ───────────────────────────────────────────
    gradcam_image = None
    if winning_model is not None and final_prediction != "Unknown":
        heatmap = make_gradcam_heatmap(arr, winning_model)
        if heatmap is not None:
            superimposed  = create_superimposed_gradcam(original_img, heatmap)
            gradcam_image = image_to_base64(superimposed)

    return {
        "final_prediction"       : final_prediction,
        "plant_part_mode"        : "mix",
        "confidence_ratio"       : confidence_ratio,
        "gradcam_image"          : gradcam_image,
        "gradcam_model"          : winning_organ,
        "individual_predictions" : individual_predictions,
    }


# =========================
# Main entry point — routes to the correct function
# =========================

def predict_image(file_bytes, plant_part="mix"):
    """
    Main predict function called by the Flask route.
    Routes to the correct model based on plant_part.
    """
    plant_part = plant_part.lower().strip()

    if plant_part == "leaf":
        return predict_leaf(file_bytes)
    elif plant_part == "bark":
        return predict_bark(file_bytes)
    elif plant_part == "cherry":
        return predict_cherry(file_bytes)
    elif plant_part == "mix":
        return predict_mix(file_bytes)
    else:
        return {
            "error"            : f"Invalid plant_part '{plant_part}'. Use: leaf, bark, cherry, mix",
            "final_prediction" : "Unknown",
            "confidence_ratio" : 0.0,
        }


# =========================
# Grad-CAM (unchanged from original)
# =========================

def make_gradcam_heatmap(img_array, model):
    try:
        layer_names = ['out_relu', 'Conv_1', 'block_16_project', 'block_16_expand']
        last_conv_layer = None

        for layer_name in layer_names:
            try:
                last_conv_layer = model.get_layer(layer_name)
                break
            except:
                continue

        if last_conv_layer is None:
            return None

        grad_model = Model(
            inputs=[model.inputs],
            outputs=[last_conv_layer.output, model.output]
        )

        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(img_array)
            if isinstance(last_conv_layer_output, list):
                last_conv_layer_output = last_conv_layer_output[0]
            if isinstance(preds, list):
                preds = preds[0]
            class_channel = preds[:, 0]

        grads = tape.gradient(class_channel, last_conv_layer_output)
        if grads is None:
            return None

        pooled_grads             = tf.reduce_mean(grads, axis=(0, 1, 2))
        last_conv_layer_output   = last_conv_layer_output.numpy()
        pooled_grads             = pooled_grads.numpy()

        if len(last_conv_layer_output.shape) == 4:
            last_conv_layer_output = last_conv_layer_output[0]

        for i in range(pooled_grads.shape[0]):
            last_conv_layer_output[:, :, i] *= pooled_grads[i]

        heatmap = np.mean(last_conv_layer_output, axis=-1)
        heatmap = np.maximum(heatmap, 0)
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()

        return heatmap

    except Exception as e:
        print(f"[ERROR] Grad-CAM failed: {e}")
        return None


def create_superimposed_gradcam(img, heatmap, alpha=0.4):
    heatmap_resized = cv2.resize(heatmap, (img.width, img.height))
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    img_array       = np.array(img)
    superimposed    = heatmap_colored * alpha + img_array * (1 - alpha)
    return np.clip(superimposed, 0, 255).astype(np.uint8)