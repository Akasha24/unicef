"""Main entry point - Start the Flask web server."""

from src.api.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("  UNICEF 15-Day Temperature Forecast System")
    print("=" * 60)
    print("\n🌡️  Server starting on http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
