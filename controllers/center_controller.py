from flask import jsonify, request
from models.models import db, CenterConfig

def get_center_config():
    """Obtener configuración del centro"""
    try:
        config = CenterConfig.query.first()
        
        if not config:
            config = CenterConfig(
                name='Centro de Salud',
                address='',
                phone='',
                email='',
                description='',
                vision=''
            )
            db.session.add(config)
            db.session.commit()
        
        return jsonify({
            'id': config.id,
            'name': config.name,
            'address': config.address,
            'phone': config.phone,
            'email': config.email,
            'description': config.description,
            'vision': config.vision,
            'logo_url': config.logo_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_center_config():
    """Actualizar configuración del centro"""
    try:
        data = request.get_json()
        config = CenterConfig.query.first()
        
        if not config:
            config = CenterConfig()
            db.session.add(config)
        
        # Actualizar campos
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
        if 'vision' in data:
            config.vision = data['vision']
        if 'logo_url' in data:
            config.logo_url = data['logo_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Configuración actualizada exitosamente',
            'config': {
                'id': config.id,
                'name': config.name,
                'address': config.address,
                'phone': config.phone,
                'email': config.email,
                'description': config.description,
                'vision': config.vision,
                'logo_url': config.logo_url
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500