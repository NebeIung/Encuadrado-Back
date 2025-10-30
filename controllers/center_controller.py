from flask import jsonify, request
from models.models import db, CenterConfig
import traceback

def get_center_config():
    """Obtener configuración del centro"""
    try:
        config = CenterConfig.query.first()
        if not config:
            # Crear configuración por defecto si no existe
            config = CenterConfig(
                name='Centro de Salud Mental',
                address='',
                phone='',
                email='',
                description=''
            )
            db.session.add(config)
            db.session.commit()
        
        return jsonify(config.to_dict()), 200
    except Exception as e:
        print(f"Error getting center config: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_center_config():
    """Actualizar configuración del centro"""
    try:
        config = CenterConfig.query.first()
        if not config:
            config = CenterConfig()
            db.session.add(config)
        
        data = request.get_json()
        
        if 'name' in data:
            config.name = data['name']
        if 'address' in data:
            config.address = data['address']
        if 'phone' in data:
            config.phone = data['phone']
        if 'email' in data:
            config.email = data['email']
        if 'description' in data:
            config.description = data['description']
        if 'logo_url' in data:
            config.logo_url = data['logo_url']
        
        db.session.commit()
        return jsonify(config.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating center config: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500