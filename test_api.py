#!/usr/bin/env python3
"""
Simple API test script to verify backend functionality
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:5000"

def test_api():
    """Test basic API endpoints"""
    
    print("Testing Mugisha Learning Platform API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return
    
    # Test registration
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "first_name": "Test",
            "last_name": "User",
            "role": "student"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            print(f"✅ Registration successful: {response.status_code}")
            token = response.json().get('token')
        else:
            print(f"⚠️  Registration: {response.status_code} - {response.json()}")
            
        # Test login
        login_data = {
            "username": "testuser",
            "password": "test123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print(f"✅ Login successful: {response.status_code}")
            token = response.json().get('token')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.json()}")
            return
            
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return
    
    # Test courses endpoint with auth
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/courses", headers=headers)
        print(f"✅ Courses endpoint: {response.status_code}")
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            print(f"   Found {len(courses)} courses")
    except Exception as e:
        print(f"❌ Courses endpoint failed: {e}")
    
    print("\n" + "=" * 50)
    print("API test completed!")
    print("Note: Make sure the Flask server is running on localhost:5000")

if __name__ == "__main__":
    test_api()
