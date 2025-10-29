import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

from flask import Flask
from config.db_config import db
from models.models import Professional, Patient, Specialty, Appointment, CenterConfig

def init_database():
    """Inicializa la base de datos con datos de prueba"""
    
    # Crear app Flask temporal
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar DB
    db.init_app(app)

    with app.app_context():
        print("🔗 Conectado a:", app.config['SQLALCHEMY_DATABASE_URI'][:50] + "...")

        try:
            # Eliminar tablas existentes
            print("🗑️  Eliminando tablas existentes...")
            db.drop_all()
            
            # Crear todas las tablas
            print("📦 Creando tablas...")
            db.create_all()
            
            print("✅ Tablas creadas correctamente")
            print("📝 Insertando datos de prueba...")

            # 1. Configuración del centro
            print("  → Configuración del centro...")
            center = CenterConfig(
                name="Centro Médico Cuad",
                description="Centro de atención médica integral con profesionales especializados en distintas áreas de la salud.",
                phone="+56912345678",
                email="contacto@centrocuad.cl",
                address="Av. Providencia 1234, Santiago",
                open_time="09:00",
                close_time="18:00"
            )
            db.session.add(center)
            db.session.flush()

            # 2. Especialidades
            print("  → Especialidades...")
            specialties = [
                Specialty(
                    name="Consulta General",
                    description="Atención médica general para diagnóstico y tratamiento",
                    duration=30,
                    price=25000
                ),
                Specialty(
                    name="Nutrición",
                    description="Evaluación nutricional y planes alimenticios personalizados",
                    duration=45,
                    price=35000
                ),
                Specialty(
                    name="Psicología",
                    description="Atención psicológica individual para adultos y adolescentes",
                    duration=60,
                    price=40000
                ),
                Specialty(
                    name="Kinesiología",
                    description="Rehabilitación física y tratamiento de lesiones",
                    duration=45,
                    price=30000
                ),
                Specialty(
                    name="Pediatría",
                    description="Atención médica especializada para niños y adolescentes",
                    duration=30,
                    price=28000
                )
            ]
            
            for specialty in specialties:
                db.session.add(specialty)
            
            db.session.flush()

            # 3. Profesionales
            print("  → Profesionales...")
            admin = Professional(
                name="Dr. Admin Principal",
                email="admin@centro.com",
                password="1234",
                role="admin",
                phone="+56987654321",
                schedule={
                    "mon": ["09:00-13:00", "14:00-18:00"],
                    "tue": ["09:00-13:00"],
                    "wed": ["14:00-18:00"],
                    "thu": ["09:00-13:00", "14:00-18:00"],
                    "fri": ["09:00-18:00"],
                    "sat": [],
                    "sun": []
                }
            )
            admin.specialties.extend([specialties[0], specialties[4]])  # Consulta General y Pediatría
            
            juan = Professional(
                name="Dr. Juan Pérez",
                email="juan@centro.com",
                password="1234",
                role="member",
                phone="+56912345678",
                schedule={
                    "mon": ["14:00-18:00"],
                    "tue": ["09:00-13:00", "14:00-18:00"],
                    "wed": ["09:00-13:00"],
                    "thu": ["09:00-13:00", "14:00-18:00"],
                    "fri": [],
                    "sat": [],
                    "sun": []
                }
            )
            juan.specialties.extend([specialties[2], specialties[1]])  # Psicología y Nutrición
            
            ana = Professional(
                name="Dra. Ana García",
                email="ana@centro.com",
                password="1234",
                role="limited",
                phone="+56923456789",
                schedule={
                    "mon": [],
                    "tue": ["09:00-18:00"],
                    "wed": ["14:00-18:00"],
                    "thu": [],
                    "fri": ["09:00-18:00"],
                    "sat": ["10:00-14:00"],
                    "sun": []
                }
            )
            ana.specialties.extend([specialties[3], specialties[1]])  # Kinesiología y Nutrición
            
            db.session.add_all([admin, juan, ana])
            db.session.flush()

            # 4. Pacientes
            print("  → Pacientes...")
            patients = [
                Patient(
                    name="Diego Pérez",
                    email="diego@email.com",
                    phone="+56934567890",
                    rut="12345678-9",
                    birth_date=datetime(1990, 5, 15).date(),
                    address="Las Condes, Santiago",
                    emergency_contact="María Pérez",
                    emergency_phone="+56945678901"
                ),
                Patient(
                    name="María Torres",
                    email="maria@email.com",
                    phone="+56956789012",
                    rut="23456789-0",
                    birth_date=datetime(1985, 8, 22).date(),
                    address="Providencia, Santiago"
                ),
                Patient(
                    name="Claudia Soto",
                    email="claudia@email.com",
                    phone="+56967890123",
                    rut="34567890-1",
                    birth_date=datetime(1992, 3, 10).date(),
                    address="Ñuñoa, Santiago",
                    notes="Alérgica a la penicilina"
                ),
                Patient(
                    name="Roberto Muñoz",
                    email="roberto@email.com",
                    phone="+56978901234",
                    rut="45678901-2",
                    birth_date=datetime(1978, 11, 5).date(),
                    address="Vitacura, Santiago"
                ),
                Patient(
                    name="Carolina López",
                    email="carolina@email.com",
                    phone="+56989012345",
                    rut="56789012-3",
                    birth_date=datetime(1995, 1, 28).date(),
                    address="La Reina, Santiago"
                )
            ]
            
            for patient in patients:
                db.session.add(patient)
            
            db.session.flush()

            # 5. Citas
            print("  → Citas...")
            today = datetime.now()
            
            appointments = [
                # Citas pasadas (completadas)
                Appointment(
                    patient_id=patients[0].id,
                    professional_id=juan.id,
                    specialty_id=specialties[2].id,  # Psicología
                    date=today - timedelta(days=5, hours=-10),
                    status="completed",
                    notes="Primera sesión completada exitosamente"
                ),
                Appointment(
                    patient_id=patients[1].id,
                    professional_id=admin.id,
                    specialty_id=specialties[0].id,  # Consulta General
                    date=today - timedelta(days=3, hours=-15),
                    status="completed"
                ),
                
                # Citas futuras (confirmadas)
                Appointment(
                    patient_id=patients[2].id,
                    professional_id=ana.id,
                    specialty_id=specialties[3].id,  # Kinesiología
                    date=today + timedelta(days=1, hours=10),
                    status="confirmed",
                    notes="Sesión de rehabilitación post-operatoria"
                ),
                Appointment(
                    patient_id=patients[0].id,
                    professional_id=juan.id,
                    specialty_id=specialties[2].id,  # Psicología
                    date=today + timedelta(days=2, hours=14),
                    status="confirmed"
                ),
                Appointment(
                    patient_id=patients[3].id,
                    professional_id=admin.id,
                    specialty_id=specialties[4].id,  # Pediatría
                    date=today + timedelta(days=3, hours=11),
                    status="confirmed"
                ),
                Appointment(
                    patient_id=patients[4].id,
                    professional_id=juan.id,
                    specialty_id=specialties[1].id,  # Nutrición
                    date=today + timedelta(days=5, hours=16),
                    status="confirmed"
                ),
                
                # Cita cancelada
                Appointment(
                    patient_id=patients[1].id,
                    professional_id=ana.id,
                    specialty_id=specialties[1].id,  # Nutrición
                    date=today + timedelta(days=7, hours=9),
                    status="cancelled",
                    cancellation_reason="Paciente enfermo, reagendar"
                )
            ]
            
            for appointment in appointments:
                db.session.add(appointment)
            
            # Commit final
            db.session.commit()
            
            print("\n✅ Base de datos inicializada exitosamente!")
            print(f"   📊 {len(specialties)} especialidades creadas")
            print(f"   👨‍⚕️ 3 profesionales creados")
            print(f"   🧑 {len(patients)} pacientes creados")
            print(f"   📅 {len(appointments)} citas creadas")
            print("\n📋 Usuarios de prueba:")
            print("   🔴 Admin: admin@centro.com / 1234")
            print("   🔵 Member: juan@centro.com / 1234")
            print("   ⚪ Limited: ana@centro.com / 1234")
            print("\n🚀 Ahora puedes ejecutar: python app.py")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al inicializar la base de datos:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    init_database()