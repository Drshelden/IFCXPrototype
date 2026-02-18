#!/usr/bin/env python
"""
API Test Suite for IFC Processing Server

This script tests all API endpoints with example queries.
Make sure the server is running first: python server.py
"""

import requests
import json
import sys
from urllib.parse import urlencode

BASE_URL = 'http://localhost:5000/api'

class Colors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_endpoint(method, endpoint, params=None, data=None, files=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, params=params, data=data, files=files)
        
        success = 200 <= response.status_code < 300
        status_color = Colors.OKGREEN if success else Colors.FAIL
        
        print(f"\n{status_color}[{response.status_code}] {method.upper()} {endpoint}{Colors.ENDC}")
        if params:
            print(f"Parameters: {json.dumps(params, indent=2)}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text}")
        
        return success
    
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}❌ Connection failed. Is the server running?{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False

def main():
    """Run API tests"""
    print(f"\n{Colors.BOLD}🧪 IFC Processing Server - API Test Suite{Colors.ENDC}")
    print("=" * 60)
    
    # Test 1: Server Status
    print(f"\n{Colors.OKBLUE}Test 1: Server Status{Colors.ENDC}")
    test_endpoint('GET', '/status')
    
    # Test 2: List Models
    print(f"\n{Colors.OKBLUE}Test 2: List Models{Colors.ENDC}")
    test_endpoint('GET', '/models')
    
    # Test 3: List Entity Types
    print(f"\n{Colors.OKBLUE}Test 3: List Entity Types{Colors.ENDC}")
    test_endpoint('GET', '/entityTypes')
    
    # Test 4: Query Entities (all)
    print(f"\n{Colors.OKBLUE}Test 4: Query All Entities{Colors.ENDC}")
    test_endpoint('GET', '/entityGuids')
    
    # Test 5: Query Entities by Model
    print(f"\n{Colors.OKBLUE}Test 5: Query Entities by Model{Colors.ENDC}")
    # First, get available models
    models_response = requests.get(f"{BASE_URL}/models")
    model_name = models_response.json()[0] if models_response.status_code == 200 and models_response.json() else 'HelloWallIFCjsonC-2x3'
    test_endpoint('GET', '/entityGuids', params={'models': model_name})
    
    # Test 6: Query Entities by Type
    print(f"\n{Colors.OKBLUE}Test 6: Query Entities by Type{Colors.ENDC}")
    test_endpoint('GET', '/entityGuids', params={'entityTypes': 'IfcPropertySet'})
    
    # Test 7: Query Component GUIDs
    print(f"\n{Colors.OKBLUE}Test 7: Query Component GUIDs{Colors.ENDC}")
    test_endpoint('GET', '/componentGuids', params={'models': model_name})
    
    # Test 8: Get Component Data
    print(f"\n{Colors.OKBLUE}Test 8: Get Component Data{Colors.ENDC}")
    # First get a GUID
    response = requests.get(f"{BASE_URL}/componentGuids", params={'models': model_name})
    if response.status_code == 200:
        data = response.json()
        if data and model_name in data and len(data[model_name]) > 0:
            guids = ','.join(data[model_name][:2])
            test_endpoint('GET', '/components', params={'componentGuids': guids})
        else:
            print(f"{Colors.WARNING}⚠️  No component GUIDs found to test{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  Could not retrieve GUIDs for testing{Colors.ENDC}")
    
    # Test 9: Refresh Memory Tree
    print(f"\n{Colors.OKBLUE}Test 9: Refresh Memory Tree{Colors.ENDC}")
    test_endpoint('POST', '/refresh')
    
    # Test 10: Complex Query
    print(f"\n{Colors.OKBLUE}Test 10: Complex Query (All Filters){Colors.ENDC}")
    test_endpoint('GET', '/componentGuids', params={
        'models': model_name,
        'entityTypes': 'IfcPropertySet'
    })
    
    print(f"\n{Colors.BOLD}=" * 60)
    print(f"Testing complete!{Colors.ENDC}\n")

if __name__ == '__main__':
    main()
