from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://catanatron:victorypoint@db:5432/catanatron_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Catan Engine!"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

# Import routes after app is created to avoid circular imports
from catanatron.web import routes
