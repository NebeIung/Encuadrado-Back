from flask import jsonify, request
from models.models import db, Professional, Specialty, ProfessionalSpecialty
from werkzeug.security import generate_password_hash
import traceback

def get_professionals():
    """Obtener todos los profesionales con información de términos"""
    try:
        include_terms = request.args.get('include_terms', 'false').lower() == 'true'
        professionals = Professional.query.all()
        return jsonify([prof.to_dict(include_terms=include_terms) for prof in professionals]), 200
    except Exception as e:
        print(f"Error getting professionals: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_professional(professional_id):
    """Obtener un profesional específico con términos"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        return jsonify(professional.to_dict(include_terms=True)), 200
    except Exception as e:
        print(f"Error getting professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def create_professional():
    """Crear un nuevo profesional"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        if Professional.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        professional = Professional(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'member'),
            schedule=data.get('schedule', {})
        )
        
        db.session.add(professional)
        db.session.commit()
        
        return jsonify(professional.to_dict(include_terms=True)), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_professional(professional_id):
    """Actualizar un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            professional.name = data['name']
        if 'email' in data:
            existing = Professional.query.filter_by(email=data['email']).first()
            if existing and existing.id != professional_id:
                return jsonify({"error": "El email ya está registrado"}), 400
            professional.email = data['email']
        if 'password' in data:
            professional.password_hash = generate_password_hash(data['password'])
        if 'role' in data:
            professional.role = data['role']
        if 'schedule' in data:
            professional.schedule = data['schedule']
        
        db.session.commit()
        return jsonify(professional.to_dict(include_terms=True)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def delete_professional(professional_id):
    """Eliminar un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        if professional.appointments:
            return jsonify({"error": "No se puede eliminar un profesional con citas asociadas"}), 400
        
        db.session.delete(professional)
        db.session.commit()
        
        return jsonify({"message": "Profesional eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def assign_specialties(professional_id):
    """
    Asignar especialidades a un profesional con términos y condiciones opcionales
    Body: {
        "specialties": [
            {
                "specialty_id": 1,
                "terms_and_conditions": "Texto opcional..."
            },
            ...
        ]
    }
    """
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        # admin@centro.com NO puede tener especialidades
        if professional.email == 'admin@centro.com':
            return jsonify({"error": "El administrador principal no puede tener especialidades asignadas"}), 400
        
        data = request.get_json()
        specialties_data = data.get('specialties', [])
        
        # Eliminar asociaciones existentes
        ProfessionalSpecialty.query.filter_by(professional_id=professional_id).delete()
        
        # Crear nuevas asociaciones
        for spec_data in specialties_data:
            specialty_id = spec_data.get('specialty_id')
            terms = spec_data.get('terms_and_conditions', '').strip()
            
            if not specialty_id:
                continue
            
            specialty = Specialty.query.get(specialty_id)
            if not specialty:
                continue
            
            # Crear asociación
            has_terms = bool(terms)
            association = ProfessionalSpecialty(
                professional_id=professional_id,
                specialty_id=specialty_id,
                terms_and_conditions=terms if terms else None,
                has_terms=has_terms,
                is_active=has_terms
            )
            db.session.add(association)
        
        db.session.commit()
        return jsonify(professional.to_dict(include_terms=True)), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error assigning specialties: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_specialty_terms(professional_id, specialty_id):
    """
    Actualizar términos y condiciones de una especialidad específica
    Body: {
        "terms_and_conditions": "Texto de términos..."
    }
    """
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        association = ProfessionalSpecialty.query.filter_by(
            professional_id=professional_id,
            specialty_id=specialty_id
        ).first()
        
        if not association:
            return jsonify({"error": "Esta especialidad no está asignada al profesional"}), 404
        
        data = request.get_json()
        terms = data.get('terms_and_conditions', '').strip()
        
        if not terms:
            return jsonify({"error": "Los términos y condiciones no pueden estar vacíos"}), 400
        
        association.terms_and_conditions = terms
        association.has_terms = True
        association.is_active = True
        
        db.session.commit()
        
        return jsonify({
            "message": "Términos actualizados exitosamente",
            "specialty": association.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating terms: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_pending_terms(professional_id):
    """Obtener especialidades sin términos y condiciones"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        pending = []
        for assoc in professional.specialty_associations:
            if not assoc.has_terms:
                specialty = Specialty.query.get(assoc.specialty_id)
                if specialty:
                    pending.append({
                        'specialty_id': specialty.id,
                        'specialty_name': specialty.name,
                        'specialty_color': specialty.color,
                        'assigned_at': assoc.created_at.isoformat() if assoc.created_at else None,
                    })
        
        return jsonify({
            'count': len(pending),
            'pending_specialties': pending
        }), 200
        
    except Exception as e:
        print(f"Error getting pending terms: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_professional_schedule(professional_id):
    """Actualizar horario de un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        schedule = data.get('schedule')
        
        if not schedule:
            return jsonify({"error": "Falta el horario"}), 400
        
        professional.schedule = schedule
        db.session.commit()
        
        return jsonify(professional.to_dict(include_terms=True)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating schedule: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500