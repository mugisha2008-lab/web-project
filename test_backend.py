# Test backend without MySQL to see what dependencies are missing
import sys

print("Testing backend dependencies...")

try:
    import flask
    print("✅ Flask: OK")
except ImportError as e:
    print(f"❌ Flask: {e}")

try:
    import flask_sqlalchemy
    print("✅ Flask-SQLAlchemy: OK")
except ImportError as e:
    print(f"❌ Flask-SQLAlchemy: {e}")

try:
    import flask_login
    print("✅ Flask-Login: OK")
except ImportError as e:
    print(f"❌ Flask-Login: {e}")

try:
    import flask_cors
    print("✅ Flask-CORS: OK")
except ImportError as e:
    print(f"❌ Flask-CORS: {e}")

try:
    import flask_migrate
    print("✅ Flask-Migrate: OK")
except ImportError as e:
    print(f"❌ Flask-Migrate: {e}")

try:
    import pyjwt
    print("✅ PyJWT: OK")
except ImportError as e:
    print(f"❌ PyJWT: {e}")

try:
    import bcrypt
    print("✅ bcrypt: OK")
except ImportError as e:
    print(f"❌ bcrypt: {e}")

try:
    import mysql.connector
    print("✅ MySQL Connector: OK")
except ImportError as e:
    print(f"❌ MySQL Connector: {e}")

print("\nBackend dependency test complete.")
