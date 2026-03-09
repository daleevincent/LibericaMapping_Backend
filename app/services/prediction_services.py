from tensorflow.keras.models import Model
import tensorflow as tf
import numpy as np
import cv2
from app.utils.image_utils import preprocess_pil_image, image_to_base64
from app.services.model_loader import load_models

MODELS = load_models()

# =========================
# Grad-CAM Implementation (FIXED)
# =========================
def make_gradcam_heatmap(img_array, model):
    """
    Generate Grad-CAM heatmap - FIXED VERSION
    """
    try:
        # Try multiple layers in order of preference
        layer_names = ['out_relu', 'Conv_1', 'block_16_project', 'block_16_expand']

        last_conv_layer = None
        last_conv_layer_name = None

        for layer_name in layer_names:
            try:
                layer = model.get_layer(layer_name)
                last_conv_layer = layer
                last_conv_layer_name = layer_name
                print(f"[INFO] Using layer '{layer_name}' for Grad-CAM")
                break
            except:
                continue

        if last_conv_layer is None:
            print("[ERROR] Could not find suitable layer")
            return None

        # Create gradient model
        grad_model = Model(
            inputs=[model.inputs],
            outputs=[last_conv_layer.output, model.output]
        )

        # Compute gradients
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(img_array)

            # Handle potential list outputs
            if isinstance(last_conv_layer_output, list):
                last_conv_layer_output = last_conv_layer_output[0]
            if isinstance(preds, list):
                preds = preds[0]

            # For binary classification
            class_channel = preds[:, 0]

        # Compute gradients
        grads = tape.gradient(class_channel, last_conv_layer_output)

        if grads is None:
            print("[ERROR] Gradients are None")
            return None

        # Convert to numpy and handle list if needed
        if isinstance(grads, list):
            grads = grads[0]
        if isinstance(last_conv_layer_output, list):
            last_conv_layer_output = last_conv_layer_output[0]

        # Pool gradients across spatial dimensions
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Convert to numpy
        last_conv_layer_output = last_conv_layer_output.numpy()
        pooled_grads = pooled_grads.numpy()

        # Get the first sample if batch
        if len(last_conv_layer_output.shape) == 4:
            last_conv_layer_output = last_conv_layer_output[0]

        # Weight the channels
        for i in range(pooled_grads.shape[0]):
            last_conv_layer_output[:, :, i] *= pooled_grads[i]

        # Create heatmap
        heatmap = np.mean(last_conv_layer_output, axis=-1)

        # Normalize
        heatmap = np.maximum(heatmap, 0)
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()

        print(f"[INFO] ✓ Heatmap generated! Shape: {heatmap.shape}, Min: {heatmap.min():.3f}, Max: {heatmap.max():.3f}")
        return heatmap

    except Exception as e:
        print(f"[ERROR] Grad-CAM generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def create_superimposed_gradcam(img, heatmap, alpha=0.4):
    """
    Superimpose the Grad-CAM heatmap on the original image
    """
    # Resize heatmap to match image size
    heatmap_resized = cv2.resize(heatmap, (img.width, img.height))

    # Convert heatmap to RGB using JET colormap
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    # Convert PIL image to numpy array
    img_array = np.array(img)

    # Superimpose: heatmap * alpha + image * (1 - alpha)
    superimposed = heatmap_colored * alpha + img_array * (1 - alpha)
    superimposed = np.clip(superimposed, 0, 255).astype(np.uint8)

    return superimposed

def predict_image(file_bytes, plant_part="mix", models=None):
    models = models or MODELS
    arr, original_img = preprocess_pil_image(file_bytes)

    liberica_votes = 0
    not_liberica_votes = 0
    winning_model = None
    winning_organ = None
    max_confidence = 0
    individual_predictions = {}

    if plant_part == "mix":
        models_to_use = models
    else:
        models_to_use = {plant_part: models[plant_part]}

    for organ, model in models_to_use.items():
        pred = model.predict(arr, verbose=0)
        liberica_prob = float(pred[0][0])
        not_liberica_prob = 1 - liberica_prob
        predicted_class = "Liberica" if liberica_prob >= 0.5 else "Not Liberica"
        confidence = max(liberica_prob, not_liberica_prob)

        individual_predictions[organ] = {
            "prediction": predicted_class,
            "confidence": round(confidence * 100, 2)
        }

        if predicted_class == "Liberica":
            liberica_votes += 1
        else:
            not_liberica_votes += 1

        if confidence > max_confidence:
            max_confidence = confidence
            winning_model = model
            winning_organ = organ

    # Final prediction & confidence ratio
    if plant_part == "mix":
        final_prediction = "Liberica" if liberica_votes >= 2 else "Not Liberica"
        total_votes = liberica_votes + not_liberica_votes
        confidence_ratio = round(max(liberica_votes, not_liberica_votes) / total_votes * 100, 2)
    else:
        final_prediction = individual_predictions[plant_part]["prediction"]
        confidence_ratio = individual_predictions[plant_part]["confidence"]

    gradcam_image = None
    if winning_model:
        heatmap = make_gradcam_heatmap(arr, winning_model)
        if heatmap is not None:
            superimposed = create_superimposed_gradcam(original_img, heatmap)
            gradcam_image = image_to_base64(superimposed)

    return {
        "final_prediction": final_prediction,
        "plant_part_mode": plant_part,  # <-- add this
        "confidence_ratio": confidence_ratio,
        "gradcam_image": gradcam_image,
        "individual_predictions": individual_predictions
    }