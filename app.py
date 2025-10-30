from flask import Flask
from flask_cors import CORS
from config.db_config import db
from routes.index import register_routes
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuración de la base de datos - USAR POSTGRESQL
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # PostgreSQL desde .env
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print(f"✓ Conectando a PostgreSQL: {DATABASE_URL.split('@')[1].split('/')[0]}")
else:
    # SQLite como fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encuadrado.db'
    print("⚠ Usando SQLite local (no hay DATABASE_URL en .env)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Registrar rutas
register_routes(app)

# Crear tablas si no existen
with app.app_context():
    db.create_all()
    print("✓ Tablas verificadas/creadas")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)