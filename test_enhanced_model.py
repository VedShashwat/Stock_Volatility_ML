import requests
import json

print("="*70)
print("TESTING ENHANCED MODEL WITH 11 FEATURES")
print("="*70)

# Test with AAPL
test_ticker = "AAPL"
print(f"\nTesting with ticker: {test_ticker}")
print("-"*70)

try:
    response = requests.post(
        "http://127.0.0.1:5000/predict",
        json={"ticker": test_ticker},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Request successful!")
        print(f"\nPrediction Results:")
        print(f"  Ticker: {data['ticker']}")
        print(f"  Date: {data['date']}")
        print(f"  Predicted Volatility: {data['prediction']}")
        print(f"  Confidence: {data['confidence']*100:.2f}%")
        print(f"\nProbability Distribution:")
        print(f"  Low: {data['probabilities']['low']*100:.2f}%")
        print(f"  Medium: {data['probabilities']['medium']*100:.2f}%")
        print(f"  High: {data['probabilities']['high']*100:.2f}%")
        print(f"\nModel Information:")
        print(f"  Algorithm: {data['model_info']['algorithm']}")
        print(f"  Features Count: {data['model_info']['features_count']}")
        print(f"  Accuracy: {data['model_info']['accuracy']*100:.2f}%")
        print(f"  F1-Score: {data['model_info']['f1_score']*100:.2f}%")
        print(f"\nTop 5 Feature Contributions:")
        for i, feature in enumerate(data['feature_contributions'][:5], 1):
            print(f"  {i}. {feature['name']:15s} → {feature['contribution']:.2f}%")
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED - ENHANCED MODEL IS WORKING!")
        print("="*70)
    else:
        print(f"✗ Request failed with status code: {response.status_code}")
        print(f"  Error: {response.text}")
        
except Exception as e:
    print(f"✗ Error occurred: {str(e)}")
    print("\nMake sure the Flask server is running at http://127.0.0.1:5000")
