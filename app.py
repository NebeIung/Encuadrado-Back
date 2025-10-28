from flask import Flask
from flask_cors import CORS
from routes.index import register_routes
from config.db_config import db

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/encuadrado_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa SQLAlchemy
db.init_app(app)

# Registra todas las rutas
register_routes(app)

@app.route('/')
def home():
    return {"message": "Backend Encuadrado funcionando 🚀"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)