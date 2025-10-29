from flask import jsonify, request
from models.models import db, CenterConfig

def get_center_config():
    config = CenterConfig.query.first()
    if not config:
        # Crear config por defecto si no existe
        config = CenterConfig(
            name="Centro Médico Cuad",
            description="Centro de salud integral",
            open_time="09:00",
            close_time="18:00"
        )
        db.session.add(config)
        db.session.commit()
    
    return jsonify(config.to_dict()), 200

def update_center_config():
    config = CenterConfig.query.first()
    data = request.get_json()
    
    if not config:
        config = CenterConfig()
        db.session.add(config)
    
    config.name = data.get('name', config.name)
    config.description = data.get('description', config.description)
    config.open_time = data.get('openTime', config.open_time)
    config.close_time = data.get('closeTime', config.close_time)
    
    db.session.commit()
    return jsonify(config.to_dict()), 200