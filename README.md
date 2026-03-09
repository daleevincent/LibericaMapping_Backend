# GeoMappingFlask Backend

A Flask-based REST API for Liberica coffee plant classification with Grad-CAM visualization and geographic mapping. Stores farm predictions in MongoDB.

---

## Features

* **Plant Classification**: Predict Liberica coffee plants using MobileNetV2 models
* **Multi-Model Analysis**: Leaf, bark, cherry, or combined (`mix`) prediction
* **Grad-CAM Visualization**: Highlights image regions influencing predictions
* **Geographic Mapping**: Save predictions with latitude and longitude
* **MongoDB Integration**: Persistent storage of farm data

---

## Directory Structure

```
GeoMappingFlask/
├── run.py                  # Application entry point
├── requirements.txt        # Dependencies
├── README.md               # Project documentation
├── .env                    # Environment variables
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Configuration (optional)
│   ├── database/
│   │   └── mongo.py        # MongoDB initialization
│   ├── models/
│   │   └── farm_model.py   # Farm data CRUD
│   ├── routes/
│   │   ├── farm_routes.py  # /farms endpoints
│   │   └── prediction_routes.py # /predict endpoint
│   ├── services/
│   │   ├── model_loader.py        # Load ML models
│   │   └── prediction_services.py # Prediction & Grad-CAM logic
│   └── utils/
│       └── image_utils.py         # Image preprocessing
└── models/
    ├── leaf_MobileNetV2_80-20_model.keras
    ├── bark_MobileNetV2_80-20_model.keras
    └── cherry_MobileNetV2_80-20_model.keras
```

---

## Setup

### Prerequisites

* Python 3.12+
* MongoDB instance (local or cloud)
* TensorFlow 2.21.0+
* Minimum 2GB RAM

### Installation

```bash
cd /path/to/GeoMappingFlask
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Create a `.env` file:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=geomapping_db
```

Start the app:

```bash
python run.py
# Server runs at http://localhost:5000
```

---

## API Endpoints

### 1. Predict Plant Classification

**POST** `/predict`
**Description:** Classifies an uploaded image and optionally saves prediction with coordinates.

**Inputs (multipart/form-data)**

| Parameter  | Type   | Required | Description                                       |
| ---------- | ------ | -------- | ------------------------------------------------- |
| file       | File   | Yes      | Image (JPG, PNG, JPEG)                            |
| plant_part | String | No       | `"leaf"`, `"bark"`, `"cherry"`, `"mix"` (default) |
| lat        | Float  | No       | Latitude (saves to DB if provided)                |
| lng        | Float  | No       | Longitude (saves to DB if provided)               |

**Output (JSON)**

```json
{
  "final_prediction": "Liberica",
  "plant_part_mode": "mix",
  "confidence_ratio": 83.33,
  "gradcam_image": "data:image/png;base64,...",
  "individual_predictions": {
    "leaf": {"prediction": "Liberica", "confidence": 92.45},
    "bark": {"prediction": "Liberica", "confidence": 78.23},
    "cherry": {"prediction": "Not Liberica", "confidence": 65.12}
  }
}
```

**Notes:** Coordinates must be provided to trigger DB save.

---

### 2. Create Farm Entry

**POST** `/farms/`
**Description:** Add farm entry manually.

**Inputs (JSON)**

```json
{
  "coordinates": {"lat": 14.5995, "lng": 120.9842},
  "prediction": "Liberica",
  "confidence_ratio": 85.5,
  "plant_part_mode": "mix",
  "farm_name": "Sample Farm",       
  "owner_id": "user123"             
}
```

**Output (JSON)**

```json
{
  "message": "Farm created"
}
```

---

### 3. Get All Farms

**GET** `/farms/`
**Description:** Retrieves all farm entries.

**Output (JSON)**

```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "coordinates": {"lat": 14.5995, "lng": 120.9842},
    "prediction": "Liberica",
    "confidence_ratio": 85.5,
    "plant_part_mode": "mix",
    "farm_name": "Sample Farm"
  }
]
```

---

## Backend Workflow

1. **App Initialization**: `create_app()` creates Flask instance, enables CORS, initializes MongoDB, loads ML models, registers routes.
2. **Prediction Workflow**: Upload image → preprocess → model inference → majority vote (if mix mode) → Grad-CAM generation → optional DB save.
3. **Database Operations**: `FarmModel.create(data)` inserts new farm; `FarmModel.get_all()` retrieves all entries.

---

## Error Responses

| Error                     | Status | Description                     |
| ------------------------- | ------ | ------------------------------- |
| No image uploaded         | 400    | Missing `file` in request       |
| Model file missing        | 500    | `.keras` file not found         |
| MongoDB connection failed | 500    | Check `MONGO_URI` and DB server |
| Unsupported image format  | 400    | Use JPG, PNG, or JPEG           |

---

## Dependencies

* Flask 3.1.3
* TensorFlow 2.21.0
* Keras 3.13.2
* PyMongo 4.16.0
* OpenCV 4.13.0
* Pillow 12.1.1
* Flask-CORS 6.0.2
* python-dotenv 1.2.2
