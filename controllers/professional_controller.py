from flask import jsonify, request
from models.models import db, Professional, Specialty

def get_professionals():
    """Obtener todos los profesionales"""
    try:
        professionals = Professional.query.filter_by(is_active=True).all()
        return jsonify([p.to_dict() for p in professionals]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_professional(professional_id):
    """Obtener un profesional específico"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_professional():
    """Crear un nuevo profesional (Solo Admin)"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('name') or not data.get('email'):
            return jsonify({"error": "Nombre y email son requeridos"}), 400
        
        # Verificar si el email ya existe
        if Professional.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        # Crear profesional
        professional = Professional(
            name=data['name'],
            email=data['email'],
            password=data.get('password', '1234'),
            role=data.get('role', 'member'),
            phone=data.get('phone'),
            schedule=data.get('schedule', {
                "mon": [], "tue": [], "wed": [], "thu": [], 
                "fri": [], "sat": [], "sun": []
            })
        )
        
        # Asignar especialidades si vienen
        if 'specialty_ids' in data:
            specialties = Specialty.query.filter(
                Specialty.id.in_(data['specialty_ids'])
            ).all()
            professional.specialties.extend(specialties)
        
        db.session.add(professional)
        db.session.commit()
        
        return jsonify(professional.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def update_professional(professional_id):
    """Actualizar un profesional (Solo Admin)"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'name' in data:
            professional.name = data['name']
        if 'email' in data:
            # Verificar que el email no esté en uso por otro profesional
            existing = Professional.query.filter_by(email=data['email']).first()
            if existing and existing.id != professional_id:
                return jsonify({"error": "El email ya está en uso"}), 400
            professional.email = data['email']
        if 'phone' in data:
            professional.phone = data['phone']
        if 'role' in data:
            professional.role = data['role']
        if 'schedule' in data:
            professional.schedule = data['schedule']
        if 'password' in data:
            professional.password = data['password']
        
        # Actualizar especialidades
        if 'specialty_ids' in data:
            professional.specialties.clear()
            specialties = Specialty.query.filter(
                Specialty.id.in_(data['specialty_ids'])
            ).all()
            professional.specialties.extend(specialties)
        
        db.session.commit()
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def delete_professional(professional_id):
    """Eliminar (desactivar) un profesional (Solo Admin)"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        # Soft delete - solo desactivar
        professional.is_active = False
        db.session.commit()
        
        return jsonify({"message": "Profesional eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def assign_specialties(professional_id):
    """Asignar especialidades a un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        specialty_ids = data.get('specialty_ids', [])
        
        # Limpiar especialidades actuales
        professional.specialties.clear()
        
        # Asignar nuevas especialidades
        if specialty_ids:
            specialties = Specialty.query.filter(
                Specialty.id.in_(specialty_ids)
            ).all()
            professional.specialties.extend(specialties)
        
        db.session.commit()
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500