import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config.db_config import db
from models.models import Professional, Patient, Specialty, Appointment, CenterConfig
from sqlalchemy import text

def init_database():
    # Create a new Flask app instance for initialization
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the db with this app
    db.init_app(app)

    with app.app_context():
        print("🔗 Conectado a:", app.config['SQLALCHEMY_DATABASE_URI'])

        try:
            # Drop and recreate all tables
            print("🗑️  Eliminando tablas existentes...")
            db.drop_all()
            db.session.commit()
            
            print("📦 Creando tablas...")
            db.create_all()
            db.session.commit()
            
            print("✅ Tablas creadas correctamente ✅")
            print("Insertando seeds...")

            # Test database connection
            db.session.execute(text('SELECT 1'))

            # 1️⃣ Configuración del centro
            center = CenterConfig(
                name="Centro Médico Cuad",
                description="Centro de atención médica integral con profesionales especializados.",
                phone="+56912345678",
                email="contacto@centrocuad.cl",
                address="Av. Providencia 1234, Santiago",
                open_time="09:00",
                close_time="18:00"
            )
            db.session.add(center)
            db.session.commit()

            # 2️⃣ Especialidades
            specialties = [
                Specialty(name="Consulta General", description="Diagnóstico general", duration=30, price=25000),
                Specialty(name="Nutrición", description="Plan alimenticio", duration=45, price=35000),
                Specialty(name="Psicología", description="Terapia individual", duration=60, price=40000),
                Specialty(name="Kinesiología", description="Rehabilitación física", duration=45, price=30000),
                Specialty(name="Pediatría", description="Niños y adolescentes", duration=30, price=28000)
            ]
            db.session.add_all(specialties)
            db.session.commit()

            # 3️⃣ Profesional admin
            admin = Professional(
                name="Dr. Admin",
                email="admin@centro.com",
                password="1234",
                role="admin",
                phone="+56987654321"
            )
            admin.specialties.extend([specialties[0], specialties[4]])
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Base de datos inicializada con éxito!")

        except Exception as e:
            db.session.rollback()
            print("❌ Error durante la inserción de datos:", str(e))
            raise

if __name__ == "__main__":
    init_database()