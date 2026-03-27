"""
Test client for the Weather Forecast API.
Provides helper functions to test all endpoints.

Usage:
    python test_api.py
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"


class APITester:
    """Helper class for testing API endpoints."""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Test /health endpoint."""
        print("\n" + "="*60)
        print("TEST: Health Check")
        print("="*60)
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Response: {json.dumps(response.json(), indent=2)}")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def get_districts(self):
        """Test /api/districts endpoint."""
        print("\n" + "="*60)
        print("TEST: Get Available Districts")
        print("="*60)
        try:
            response = self.session.get(f"{self.base_url}/api/districts")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Available districts: {data['count']}")
            print(f"  {', '.join(data['districts'][:3])}...")
            return data.get('districts', [])
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    def get_model_info(self, district):
        """Test /api/model-info/<district> endpoint."""
        print("\n" + "="*60)
        print(f"TEST: Get Model Info for '{district}'")
        print("="*60)
        try:
            response = self.session.get(
                f"{self.base_url}/api/model-info/{district}"
            )
            response.raise_for_status()
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            if data['status'] == 'success':
                info = data['data']
                print(f"✓ Model exists: {info['model_exists']}")
                print(f"✓ Scalers exist: {info['scalers_exist']}")
                print(f"✓ Model size: {info['model_size_mb']:.2f} MB")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def predict(self, district, date_str=None):
        """Test /api/predict endpoint."""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        print("\n" + "="*60)
        print(f"TEST: Single Prediction")
        print("="*60)
        print(f"  District: {district}")
        print(f"  Date: {date_str}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/predict",
                json={"district": district, "date": date_str},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                print(f"✓ Status: {response.status_code}")
                print(f"✓ Predictions generated: {len(data['predictions'])} days")
                print(f"✓ First prediction: {data['predictions'][0]['date']} → {data['predictions'][0]['tmax']}°C")
                print(f"✓ Last prediction: {data['predictions'][-1]['date']} → {data['predictions'][-1]['tmax']}°C")
                return True
            else:
                print(f"✗ API Error: {data.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def predict_batch(self, requests_list):
        """Test /api/predict-batch endpoint."""
        print("\n" + "="*60)
        print(f"TEST: Batch Prediction ({len(requests_list)} requests)")
        print("="*60)
        for i, req in enumerate(requests_list, 1):
            print(f"  {i}. {req['district']} on {req['date']}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/predict-batch",
                json={"requests": requests_list},
                timeout=60
            )
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Successful: {data['successful']}/{len(requests_list)}")
            print(f"✓ Failed: {data['failed']}/{len(requests_list)}")
            
            if data['errors']:
                print(f"\n✗ Errors:")
                for err in data['errors']:
                    print(f"   Request {err['index']}: {err['error']}")
            
            return data['successful'] > 0
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def test_invalid_district(self):
        """Test error handling with invalid district."""
        print("\n" + "="*60)
        print("TEST: Invalid District (Error Handling)")
        print("="*60)
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/predict",
                json={"district": "invalid_dist", "date": "2026-03-26"}
            )
            data = response.json()
            
            if response.status_code == 400:
                print(f"✓ Correct status code: {response.status_code}")
                print(f"✓ Error message: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"✗ Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def test_invalid_date_format(self):
        """Test error handling with invalid date format."""
        print("\n" + "="*60)
        print("TEST: Invalid Date Format (Error Handling)")
        print("="*60)
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/predict",
                json={"district": "beed", "date": "03/26/2026"}
            )
            data = response.json()
            
            if response.status_code == 400:
                print(f"✓ Correct status code: {response.status_code}")
                print(f"✓ Error message: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"✗ Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def run_full_test_suite(self):
        """Run all tests."""
        print("\n" + "█"*60)
        print("█" + " "*58 + "█")
        print("█  WEATHER FORECAST API - FULL TEST SUITE" + " "*18 + "█")
        print("█" + " "*58 + "█")
        print("█"*60)
        
        results = {}
        
        # Basic tests
        results['health_check'] = self.health_check()
        districts = self.get_districts()
        
        if not districts:
            print("\n✗ No districts available. Skipping remaining tests.")
            return results
        
        # Model info test
        results['model_info'] = self.get_model_info(districts[0])
        
        # Single prediction
        today = datetime.now().strftime("%Y-%m-%d")
        results['single_prediction'] = self.predict(districts[0], today)
        
        # Batch prediction
        batch_requests = [
            {"district": districts[0], "date": today},
        ]
        if len(districts) > 1:
            batch_requests.append({"district": districts[1], "date": today})
        results['batch_prediction'] = self.predict_batch(batch_requests)
        
        # Error handling
        results['invalid_district'] = self.test_invalid_district()
        results['invalid_date'] = self.test_invalid_date_format()
        
        # Summary
        print("\n" + "█"*60)
        print("█  TEST SUMMARY" + " "*45 + "█")
        print("█"*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status:>8} | {test_name}")
        
        print("█"*60)
        print(f"  {passed}/{total} tests passed")
        print("█"*60 + "\n")
        
        return results


def main():
    """Run full test suite."""
    print("\nConnecting to API at:", BASE_URL)
    print("Make sure 'python app.py' is running in another terminal\n")
    
    tester = APITester(BASE_URL)
    
    try:
        # Quick connectivity check
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        response.raise_for_status()
    except Exception as e:
        print(f"✗ Cannot connect to API at {BASE_URL}")
        print(f"  Error: {e}")
        print("\n  Start the API with: python app.py")
        return
    
    # Run full test suite
    tester.run_full_test_suite()


if __name__ == "__main__":
    main()
