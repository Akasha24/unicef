"""
Configuration management for the Weather Forecast API.
Centralized settings for the Flask app and model management.
"""

import os
from pathlib import Path

# Get the directory of this script
BASE_DIR = Path(__file__).parent

# ============================================================
# FLASK CONFIGURATION
# ============================================================

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max request size


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


# ============================================================
# API CONFIGURATION
# ============================================================

# Available districts and their coordinates
DISTRICT_COORDINATES = {
    "beed": {"lat": 18.9901, "lon": 75.7531},
    "Chhatrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433},
    "Dhule": {"lat": 20.9042, "lon": 74.7749},
    "Jalgaon": {"lat": 21.0077, "lon": 75.5626},
    "Jalna": {"lat": 19.8410, "lon": 75.8864},
    "Wardha": {"lat": 20.7453, "lon": 78.6022},
    "Yavatmal": {"lat": 20.3899, "lon": 78.1307},
}

# Prediction window
FORECAST_HORIZON = 15  # Days to forecast

# Feature columns used in training
FEATURE_COLUMNS = [
    'msl',
    'wind_speed',
    'solar_radiation',
    'relative_humidity',
    'rainfall',
    'month'
]

# Target column
TARGET_COLUMN = 'tmax'

# ============================================================
# MODEL CONFIGURATION
# ============================================================

# Model artifact extensions
MODEL_EXTENSION = '.keras'
SCALER_EXTENSION = '.pkl'

# Model file naming pattern
def get_model_filename(district: str) -> str:
    """Get model filename for a district."""
    safe_name = district.lower().replace(" ", "_")
    return f"{safe_name}_model{MODEL_EXTENSION}"


def get_scaler_filename(district: str) -> str:
    """Get scaler filename for a district."""
    safe_name = district.lower().replace(" ", "_")
    return f"{safe_name}_scalers{SCALER_EXTENSION}"


# ============================================================
# API CONFIGURATION
# ============================================================

# Open-Meteo API URLs
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Archive threshold: if date is older than this, use archive API
ARCHIVE_CUTOFF_DAYS = 2

# ============================================================
# TIMEOUT & RETRY CONFIGURATION
# ============================================================

API_REQUEST_TIMEOUT = 30  # Seconds
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 1  # Seconds

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# ============================================================
# ENVIRONMENT-SPECIFIC CONFIG SELECTION
# ============================================================

def get_config(env: str = None) -> Config:
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_model_path(district: str) -> Path:
    """Get full path to model file."""
    return BASE_DIR / get_model_filename(district)


def get_scaler_path(district: str) -> Path:
    """Get full path to scaler file."""
    return BASE_DIR / get_scaler_filename(district)


def validate_district(district_input: str) -> str:
    """
    Validate and normalize district name.
    Returns the canonical district name.
    Raises ValueError if not found.
    """
    for key in DISTRICT_COORDINATES.keys():
        if key.lower() == district_input.lower():
            return key
    
    raise ValueError(
        f"District '{district_input}' not found. "
        f"Available: {', '.join(DISTRICT_COORDINATES.keys())}"
    )
