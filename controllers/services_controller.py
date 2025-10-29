from flask import jsonify, request
from models.models import db, Specialty

def get_services():
    specialties = Specialty.query.filter_by(is_active=True).all()
    return jsonify([s.to_dict() for s in specialties]), 200

def create_service():
    data = request.get_json()
    
    specialty = Specialty(
        name=data['name'],
        duration=data.get('duration', 30),
        price=data.get('price', 0),
        description=data.get('description')
    )
    
    db.session.add(specialty)
    db.session.commit()
    
    return jsonify(specialty.to_dict()), 201

def update_service(service_id):
    specialty = Specialty.query.get(service_id)
    if not specialty:
        return jsonify({"error": "No encontrado"}), 404
    
    data = request.get_json()
    specialty.name = data.get('name', specialty.name)
    specialty.duration = data.get('duration', specialty.duration)
    specialty.price = data.get('price', specialty.price)
    specialty.description = data.get('description', specialty.description)
    
    db.session.commit()
    return jsonify(specialty.to_dict()), 200

def delete_service(service_id):
    specialty = Specialty.query.get(service_id)
    if not specialty:
        return jsonify({"error": "No encontrado"}), 404
    
    specialty.is_active = False
    db.session.commit()
    return jsonify({"message": "Eliminado"}), 200