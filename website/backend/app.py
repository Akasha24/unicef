"""Simple Flask API that exposes a prediction endpoint.

Endpoint: POST /predict
Payload: { "district": "beed", "date": "YYYY-MM-DD" }
Response: JSON list of 15 predicted Tmax values with dates.
"""

from __future__ import annotations

from flask import Flask, request, jsonify
import traceback

try:
    from website.backend.pipeline import _lookup_district_key, predict_for_district
except Exception:
    from pipeline import _lookup_district_key, predict_for_district
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(force=True)
        district = payload.get("district")
        date_str = payload.get("date")

        if not district or not date_str:
            return jsonify({"error": "'district' and 'date' fields are required"}), 400

        # validate district
        key = _lookup_district_key(district)
        if not key:
            return jsonify({"error": f"Unknown district: {district}"}), 400

        results_df, _ = predict_for_district(district, date_str)

        records = results_df.to_dict(orient="records")
        return jsonify({"predictions": records}), 200

    except Exception as exc:
        logger.exception("Prediction API failed: %s", exc)
        return jsonify(
            {
                "error": "internal server error",
                "detail": str(exc),
                "trace": traceback.format_exc(),
            }
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)