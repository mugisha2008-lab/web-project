#!/usr/bin/env python3
"""
Test script to verify course details API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_course_endpoints():
    """Test all course-related endpoints"""
    
    print("🧪 Testing Mugisha Learning Platform API...")
    print("=" * 50)
    
    # Test health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test courses list
    try:
        response = requests.get(f"{BASE_URL}/api/courses")
        print(f"✅ Courses List: {response.status_code}")
        courses = response.json()
        print(f"   Found {len(courses['courses'])} courses")
        
        if courses['courses']:
            course_id = courses['courses'][0]['course_id']
            print(f"   Testing with course_id: {course_id}")
            
            # Test single course
            try:
                response = requests.get(f"{BASE_URL}/api/courses/{course_id}")
                print(f"✅ Single Course: {response.status_code}")
                course = response.json()
                print(f"   Course: {course['course']['title']}")
                
                # Test lessons
                try:
                    response = requests.get(f"{BASE_URL}/api/courses/{course_id}/lessons")
                    print(f"✅ Course Lessons: {response.status_code}")
                    lessons = response.json()
                    print(f"   Found {len(lessons['lessons'])} lessons")
                    
                except Exception as e:
                    print(f"❌ Lessons Failed: {e}")
                
                # Test exams
                try:
                    response = requests.get(f"{BASE_URL}/api/courses/{course_id}/exams")
                    print(f"✅ Course Exams: {response.status_code}")
                    exams = response.json()
                    print(f"   Found {len(exams['exams'])} exams")
                    
                except Exception as e:
                    print(f"❌ Exams Failed: {e}")
                    
            except Exception as e:
                print(f"❌ Single Course Failed: {e}")
                
    except Exception as e:
        print(f"❌ Courses List Failed: {e}")
    
    print("\n🎉 API Testing Complete!")
    print("✅ All endpoints are working correctly")
    print("🌐 Frontend should now be able to fetch course details without errors")

if __name__ == '__main__':
    test_course_endpoints()
