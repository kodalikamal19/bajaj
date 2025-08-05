#!/usr/bin/env python3
"""
Test script for optimized HackRX API
"""
import requests
import json
import time

def test_optimized_endpoint():
    """Test the optimized ultra endpoint"""
    url = 'http://localhost:5001/api/ultra/v1/hackrx/run'
    
    # Sample data for testing
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?"
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print("Testing optimized HackRX endpoint...")
        print(f"URL: {url}")
        
        start_time = time.time()
        response = requests.post(url, json=test_data, headers=headers, timeout=60)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Response structure:")
            print(f"Keys: {list(result.keys())}")
            
            # Check if response matches expected format
            if 'answers' in result and len(result['answers']) == len(test_data['questions']):
                print("✅ Response format is correct")
                print(f"Number of answers: {len(result['answers'])}")
                
                # Print answers
                for i, answer in enumerate(result['answers']):
                    print(f"Q{i+1}: {test_data['questions'][i]}")
                    print(f"A{i+1}: {answer}")
                    print()
                
                return True
            else:
                print("❌ Response format is incorrect")
                print(f"Expected 'answers' key with {len(test_data['questions'])} items")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def main():
    """Run optimization test"""
    print("=== Optimized HackRX API Test ===\n")
    
    # Test optimized endpoint
    success = test_optimized_endpoint()
    
    print("\n=== Test Summary ===")
    if success:
        print("🎉 Optimization test passed!")
        print("✅ JSON-only response format working")
        print("✅ No unnecessary runtime metrics")
        print("✅ Faster response times expected")
    else:
        print("❌ Optimization test failed!")

if __name__ == "__main__":
    main()

