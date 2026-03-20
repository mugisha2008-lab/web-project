from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Simple health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Mugisha Learning Platform Backend is running!',
        'version': '1.0.0'
    })

# Simple API info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    return jsonify({
        'name': 'Mugisha Learning Platform API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'courses': '/api/courses (when database is connected)',
            'auth': '/api/auth/* (when database is connected)'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Mugisha Learning Platform Backend...")
    print("📍 Server will run on: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("📚 API info: http://localhost:5000/api/info")
    print("⚠️  Note: Full database features require MySQL setup")
    print("\n🎯 Frontend is running at: http://localhost:3000")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
