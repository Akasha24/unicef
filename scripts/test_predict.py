"""Test prediction script - Run forecasts from CLI."""

from src.ml.pipeline import predict_for_district
import sys


def test_predict():
    """Test prediction for beed district."""
    district = sys.argv[1] if len(sys.argv) > 1 else "beed"
    date_str = sys.argv[2] if len(sys.argv) > 2 else "2025-09-11"
    
    print(f"\nTesting prediction for {district} on {date_str}...")
    print("-" * 60)
    
    try:
        results_df, rmse_df = predict_for_district(district, date_str)
        
        print("\n15-DAY FORECAST:")
        print(results_df.to_string(index=False))
        
        print("\nFORECAST WITH METRICS (Actual Tmax & RMSE):")
        print(rmse_df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_predict()
