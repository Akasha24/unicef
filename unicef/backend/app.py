"""
Weather Forecast Backend API
Provides endpoints for temperature prediction using pre-trained models.

Usage:
    python app.py

Then access the API at http://localhost:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from models import ModelManager
import traceback
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure CORS with explicit settings
CORS(app, 
     origins="*",
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     expose_headers=["Content-Type"],
     supports_credentials=False,
     max_age=3600)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize model manager
model_manager = ModelManager()


# ============================================================
# HEALTH CHECK & INFO ENDPOINTS
# ============================================================

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint."""
    if request.method == 'OPTIONS':
        return '', 200
    logger.info('Health check requested')
    return jsonify({
        "status": "healthy",
        "service": "weather-forecast-api",
        "version": "1.0.0"
    }), 200


@app.route('/api/districts', methods=['GET', 'OPTIONS'])
def get_districts():
    """Get list of available districts."""
    if request.method == 'OPTIONS':
        return '', 200
    try:
        logger.info('Districts list requested')
        districts = model_manager.get_available_districts()
        response_data = {
            "status": "success",
            "districts": districts,
            "count": len(districts)
        }
        logger.info(f'Returning {len(districts)} districts')
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error fetching districts: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/model-info/<district>', methods=['GET', 'OPTIONS'])
def get_model_info(district):
    """Get information about a trained model."""
    if request.method == 'OPTIONS':
        return '', 200
    try:
        logger.info(f'Model info requested for district: {district}')
        info = model_manager.get_model_info(district)
        if "error" in info:
            logger.warning(f'Model not found for district: {district}')
            return jsonify({"status": "error", "message": info["error"]}), 400
        return jsonify({"status": "success", "data": info}), 200
    except Exception as e:
        logger.error(f"Error fetching model info: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """
    Generate 15-day temperature forecast.
    
    Request body (JSON):
    {
        "district": "beed",
        "date": "2026-03-26"
    }
    
    Response:
    {
        "status": "success",
        "district": "beed",
        "base_date": "2026-03-26",
        "predictions": [
            {"day": 1, "date": "2026-03-27", "tmax": 35.42},
            ...
        ]
    }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Parse request
        data = request.get_json(force=True, silent=True)
        
        if not data:
            logger.warning('Empty JSON body received')
            return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
        
        district = data.get('district', '').strip()
        date_str = data.get('date', '').strip()
        
        # Validate inputs
        if not district:
            return jsonify({"status": "error", "message": "District is required"}), 400
        
        if not date_str:
            return jsonify({"status": "error", "message": "Date is required (format: YYYY-MM-DD)"}), 400
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid date format. Use YYYY-MM-DD"
            }), 400
        
        logger.info(f"Prediction request: district={district}, date={date_str}")
        
        # Generate prediction
        result = model_manager.predict(date_str, district)
        
        logger.info(f"Prediction successful for {district}")
        return jsonify(result), 200
    
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Validation error: {error_msg}")
        return jsonify({"status": "error", "message": error_msg}), 400
    
    except FileNotFoundError as e:
        error_msg = str(e)
        logger.error(f"Model file not found: {error_msg}")
        return jsonify({
            "status": "error",
            "message": f"Model files not found. {error_msg}"
        }), 404
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": f"Prediction failed: {str(e)}"
        }), 500


# ============================================================
# BATCH PREDICTION ENDPOINT
# ============================================================

@app.route('/api/predict-batch', methods=['POST'])
def predict_batch():
    """
    Generate forecasts for multiple districts and/or dates.
    
    Request body (JSON):
    {
        "requests": [
            {"district": "beed", "date": "2026-03-26"},
            {"district": "dhule", "date": "2026-03-26"}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'requests' not in data:
            return jsonify({
                "status": "error",
                "message": "Request body must contain 'requests' array"
            }), 400
        
        requests_list = data.get('requests', [])
        
        if not isinstance(requests_list, list):
            return jsonify({
                "status": "error",
                "message": "'requests' must be an array"
            }), 400
        
        if len(requests_list) == 0:
            return jsonify({
                "status": "error",
                "message": "Requests array cannot be empty"
            }), 400
        
        results = []
        errors = []
        
        for i, req in enumerate(requests_list):
            try:
                district = req.get('district', '').strip()
                date_str = req.get('date', '').strip()
                
                if not district or not date_str:
                    errors.append({
                        "index": i,
                        "error": "District and date are required"
                    })
                    continue
                
                result = model_manager.predict(date_str, district)
                results.append({
                    "index": i,
                    "data": result
                })
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e)
                })
        
        return jsonify({
            "status": "partial_success" if errors else "success",
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }), 200 if not errors else 207
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Batch prediction failed: {str(e)}"
        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed."""
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"500 Internal Server Error: {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    logger.info("Starting Weather Forecast API...")
    logger.info("Available districts: {}".format(
        ", ".join(model_manager.get_available_districts())
    ))
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
