"""Flask API for temperature forecasting.

Endpoint: POST /predict
Payload: { "district": "beed", "date": "YYYY-MM-DD" }
Response: JSON with predictions and metrics
"""

from __future__ import annotations

from flask import Flask, request, jsonify, send_from_directory
import os
import traceback
import logging

try:
    from src.ml.pipeline import _lookup_district_key, predict_for_district
except Exception:
    from ..ml.pipeline import _lookup_district_key, predict_for_district

logger = logging.getLogger(__name__)

# Get paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATIC_DIR = os.path.join(REPO_ROOT, "src", "frontend", "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

try:
    from flask_cors import CORS
    CORS(app)
except Exception:
    pass


@app.route("/")
def index():
    """Serve the main HTML page."""
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Prediction endpoint: POST /predict"""
    try:
        payload = request.get_json(force=True)
        district = payload.get("district")
        date_str = payload.get("date")

        if not district or not date_str:
            return jsonify({"error": "'district' and 'date' fields are required"}), 400

        key = _lookup_district_key(district)
        if not key:
            return jsonify({"error": f"Unknown district: {district}"}), 400

        results_df, rmse_df = predict_for_district(district, date_str)

        records = results_df.to_dict(orient="records")
        rmse_records = rmse_df.to_dict(orient="records")
        return jsonify({"predictions": records, "metrics": rmse_records}), 200

    except Exception as exc:
        logger.exception("Prediction API failed: %s", exc)
        return jsonify({
            "error": "internal server error",
            "detail": str(exc),
            "trace": traceback.format_exc(),
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
