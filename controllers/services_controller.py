from flask import jsonify, request
from models.models import db, Specialty
import traceback
import re

def is_valid_hex_color(color):
    """Validar que el color sea un código hexadecimal válido"""
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))

def get_services():
    """Obtener todas las especialidades/servicios con contador de profesionales"""
    try:
        specialties = Specialty.query.all()
        return jsonify([specialty.to_dict(include_professionals=True) for specialty in specialties]), 200
    except Exception as e:
        print(f"Error getting services: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def create_service():
    """Crear un nuevo servicio"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('duration') or not data.get('price'):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        # Validar color
        color = data.get('color', '#1976d2')
        if not is_valid_hex_color(color):
            return jsonify({"error": "Color inválido. Debe ser un código hexadecimal (#RRGGBB)"}), 400
        
        service = Specialty(
            name=data['name'],
            description=data.get('description', ''),
            duration=int(data['duration']),
            price=float(data['price']),
            color=color
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify(service.to_dict(include_professionals=True)), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating service: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_service(service_id):
    """Actualizar un servicio existente"""
    try:
        service = Specialty.query.get(service_id)
        if not service:
            return jsonify({"error": "Servicio no encontrado"}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'duration' in data:
            service.duration = int(data['duration'])
        if 'price' in data:
            service.price = float(data['price'])
        if 'color' in data:
            if not is_valid_hex_color(data['color']):
                return jsonify({"error": "Color inválido. Debe ser un código hexadecimal (#RRGGBB)"}), 400
            service.color = data['color']
        
        db.session.commit()
        return jsonify(service.to_dict(include_professionals=True)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating service: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def delete_service(service_id):
    """Eliminar un servicio"""
    try:
        service = Specialty.query.get(service_id)
        if not service:
            return jsonify({"error": "Servicio no encontrado"}), 404
        
        # Verificar si hay citas asociadas
        if service.appointments:
            return jsonify({"error": "No se puede eliminar un servicio con citas asociadas"}), 400
        
        # Verificar si hay profesionales asignados (excluyendo admins)
        non_admin_professionals = [p for p in service.professionals if p.role != 'admin']
        if non_admin_professionals:
            return jsonify({
                "error": f"No se puede eliminar. Hay {len(non_admin_professionals)} profesional(es) asignado(s) a esta especialidad."
            }), 400
        
        db.session.delete(service)
        db.session.commit()
        
        return jsonify({"message": "Servicio eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting service: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500