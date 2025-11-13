"""Main Flask application entry point."""
from flask import Flask
from flask_cors import CORS
from routes import register_blueprints

# Initialize Flask application
app = Flask(__name__, static_folder='static')

# Configure CORS
CORS(app, origins=["http://localhost:3000", "https://react-client-p2v3.onrender.com"], methods=["GET", "POST", "OPTIONS"])

# Register route blueprints
register_blueprints(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
