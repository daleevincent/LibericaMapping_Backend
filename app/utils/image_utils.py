from PIL import Image
import numpy as np
import io
import base64


def preprocess_pil_image(file_bytes, target_size=(224, 224)):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize(target_size)

    arr = np.array(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)

    return arr, img


def image_to_base64(img_array):
    img = Image.fromarray(img_array)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"