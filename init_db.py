from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

from flask import Flask
from config.db_config import db
from models.models import Professional, Patient, Specialty, Appointment, CenterConfig

def init_database():
    """Inicializa la base de datos con datos de prueba"""
    app = Flask(__name__)
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        print(f"✓ Conectando a PostgreSQL: {DATABASE_URL.split('@')[1].split('/')[0]}")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encuadrado.db'
        print("⚠ Usando SQLite local (no hay DATABASE_URL en .env)")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.drop_all()
        print("✓ Tablas eliminadas")
        
        db.create_all()
        print("✓ Tablas creadas")
        
        # Crear especialidades
        especialidades = [
            Specialty(
                name='Psicología',
                description='Atención psicológica individual para diagnóstico y tratamiento',
                duration=60,
                price=50000,
                color='#1976d2'
            ),
            Specialty(
                name='Psiquiatría',
                description='Evaluación psiquiátrica y seguimiento médico especializado',
                duration=45,
                price=70000,
                color='#d32f2f'
            ),
            Specialty(
                name='Terapia de Pareja',
                description='Orientación y terapia para parejas',
                duration=90,
                price=80000,
                color='#9c27b0'
            ),
            Specialty(
                name='Terapia Familiar',
                description='Terapia sistémica familiar',
                duration=90,
                price=75000,
                color='#ed6c02'
            ),
            Specialty(
                name='Neuropsicología',
                description='Evaluación y rehabilitación neuropsicológica',
                duration=60,
                price=65000,
                color='#2e7d32'
            ),
        ]
        
        for esp in especialidades:
            db.session.add(esp)
        db.session.commit()
        print(f"✓ {len(especialidades)} especialidades creadas")
        
        from werkzeug.security import generate_password_hash
        
        # Horario estándar para Psicología (lunes a viernes)
        horario_psicologia = {
            "mon": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "tue": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "wed": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "thu": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "fri": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "sat": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""},
            "sun": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        # Horario para Psiquiatría (incluye sábado)
        horario_psiquiatria = {
            "mon": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "tue": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "wed": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "thu": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "fri": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "sat": {"enabled": True, "start": "09:00", "end": "13:00", "lunch_start": "", "lunch_end": ""},
            "sun": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        # Horario para Terapias (tardes)
        horario_terapias = {
            "mon": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "tue": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "wed": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "thu": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "fri": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "sat": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""},
            "sun": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        profesionales = [
            # Admin sin especialidades ni horarios
            Professional(
                name='Administrador Centro',
                email='admin@centro.com',
                password_hash=generate_password_hash('1234'),
                role='admin',
                schedule={}  # Admin no tiene horarios
            ),
            # Member con horarios por especialidad
            Professional(
                name='Juan Pérez',
                email='juan@centro.com',
                password_hash=generate_password_hash('1234'),
                role='member',
                schedule={
                    "3": horario_terapias,  # Terapia de Pareja
                    "4": horario_terapias,  # Terapia Familiar
                }
            ),
            # Limited con horarios por especialidad
            Professional(
                name='Ana García',
                email='ana@centro.com',
                password_hash=generate_password_hash('1234'),
                role='limited',
                schedule={
                    "1": horario_psicologia,    # Psicología
                    "5": horario_psiquiatria,  # Neuropsicología (diferentes horarios)
                }
            ),
        ]
        
        for prof in profesionales:
            db.session.add(prof)
        db.session.commit()
        print(f"✓ {len(profesionales)} profesionales creados")
        
        # Asignar especialidades (Admin NO tiene especialidades)
        profesionales[1].specialties.extend([especialidades[2], especialidades[3]])  # Juan: Terapias
        profesionales[2].specialties.extend([especialidades[0], especialidades[4]])  # Ana: Psicología y Neuro
        db.session.commit()
        print("✓ Especialidades asignadas a profesionales")
        
        # Crear pacientes
        pacientes = [
            Patient(
                name='María López',
                email='maria.lopez@email.com',
                phone='+56912345678',
                rut='12345678-9',
                birth_date=datetime(1990, 5, 15)
            ),
            Patient(
                name='Pedro Sánchez',
                email='pedro.sanchez@email.com',
                phone='+56923456789',
                rut='23456789-0',
                birth_date=datetime(1985, 8, 20)
            ),
            Patient(
                name='Laura Fernández',
                email='laura.fernandez@email.com',
                phone='+56934567890',
                rut='34567890-1',
                birth_date=datetime(1992, 3, 10)
            ),
            Patient(
                name='Roberto Torres',
                email='roberto.torres@email.com',
                phone='+56945678901',
                rut='45678901-2',
                birth_date=datetime(1988, 11, 25)
            ),
        ]
        
        for paciente in pacientes:
            db.session.add(paciente)
        db.session.commit()
        print(f"✓ {len(pacientes)} pacientes creados")
        
        # Crear citas de ejemplo
        hoy = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
        
        citas = [
            # Citas para Juan (Terapias en horario de tarde)
            Appointment(
                patient_id=pacientes[0].id,
                professional_id=profesionales[1].id,
                specialty_id=especialidades[2].id,  # Terapia de Pareja
                date=hoy,
                status='confirmed',
                notes='Terapia de pareja - Sesión 3'
            ),
            # Citas para Ana (Psicología en horario de mañana)
            Appointment(
                patient_id=pacientes[1].id,
                professional_id=profesionales[2].id,
                specialty_id=especialidades[0].id,  # Psicología
                date=hoy.replace(hour=10),
                status='confirmed',
                notes='Primera consulta psicológica'
            ),
        ]
        
        for cita in citas:
            db.session.add(cita)
        db.session.commit()
        print(f"✓ {len(citas)} citas creadas")
        
        # Crear configuración del centro
        config = CenterConfig(
            name='Centro de Salud Mental Encuadrado',
            address='Av. Principal 123, Santiago',
            phone='+56912345678',
            email='contacto@encuadrado.cl',
            description='Centro especializado en salud mental y bienestar psicológico'
        )
        db.session.add(config)
        db.session.commit()
        print("✓ Configuración del centro creada")
        
        print("\n" + "="*50)
        print("✓ Base de datos inicializada correctamente")
        print(f"✓ Base de datos: {'PostgreSQL (Aiven)' if DATABASE_URL else 'SQLite Local'}")
        print("="*50)
        print("\nCredenciales de acceso:")
        print("  Admin (sin especialidades):")
        print("    Email: admin@centro.com")
        print("    Password: 1234")
        print("\n  Member (Terapias tardes):")
        print("    Email: juan@centro.com")
        print("    Password: 1234")
        print("\n  Limited (Psicología/Neuro):")
        print("    Email: ana@centro.com")
        print("    Password: 1234")
        print("="*50)


if __name__ == "__main__":
    init_database()