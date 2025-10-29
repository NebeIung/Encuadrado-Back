from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from config.db_config import db
import os

# Cargar variables desde .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuración de Base de Datos
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("❌ DATABASE_URL no encontrada en el archivo .env")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializamos DB
    db.init_app(app)

    # Registrar rutas
    from routes.index import register_routes
    register_routes(app)

    @app.route("/")
    def home():
        return {"message": "✅ Backend conectado a Aiven PostgreSQL 🚀"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)