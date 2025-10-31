from flask import Flask, request, jsonify, send_from_directory
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend

@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'World')
    return jsonify({'message': f'Hello, {name}!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from datetime import datetime, timedelta
import bcrypt
import os

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prescriptions = db.relationship('Prescription', backref='user', lazy=True)
    admissions = db.relationship('Admission', backref='user', lazy=True)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_number = db.Column(db.String(20))
    admission_date = db.Column(db.DateTime)
    discharge_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Routes for serving frontend files
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'code3.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# API Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        phone=data.get('phone', '')
    )
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/prescriptions', methods=['GET'])
@jwt_required()
def get_prescriptions():
    user_id = get_jwt_identity()
    prescriptions = Prescription.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': p.id,
        'medication_name': p.medication_name,
        'dosage': p.dosage,
        'frequency': p.frequency,
        'duration': p.duration,
        'status': p.status,
        'notes': p.notes,
        'created_at': p.created_at.isoformat()
    } for p in prescriptions])

@app.route('/api/prescriptions', methods=['POST'])
@jwt_required()
def create_prescription():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    prescription = Prescription(
        user_id=user_id,
        medication_name=data['medication_name'],
        dosage=data['dosage'],
        frequency=data['frequency'],
        duration=data['duration'],
        notes=data.get('notes', '')
    )
    db.session.add(prescription)
    db.session.commit()
    
    return jsonify({
        'id': prescription.id,
        'medication_name': prescription.medication_name,
        'status': prescription.status
    }), 201

@app.route('/api/admissions', methods=['GET'])
@jwt_required()
def get_admissions():
    user_id = get_jwt_identity()
    admissions = Admission.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': a.id,
        'room_number': a.room_number,
        'admission_date': a.admission_date.isoformat() if a.admission_date else None,
        'discharge_date': a.discharge_date.isoformat() if a.discharge_date else None,
        'status': a.status,
        'notes': a.notes,
        'created_at': a.created_at.isoformat()
    } for a in admissions])

@app.route('/api/admissions', methods=['POST'])
@jwt_required()
def create_admission():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    admission = Admission(
        user_id=user_id,
        room_number=data['room_number'],
        admission_date=datetime.fromisoformat(data['admission_date']) if data.get('admission_date') else None,
        discharge_date=datetime.fromisoformat(data['discharge_date']) if data.get('discharge_date') else None,
        status=data['status'],
        notes=data.get('notes', '')
    )
    db.session.add(admission)
    db.session.commit()
    
    return jsonify({
        'id': admission.id,
        'room_number': admission.room_number,
        'status': admission.status
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
