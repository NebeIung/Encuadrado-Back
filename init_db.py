from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

from flask import Flask
from config.db_config import db
from models.models import Professional, Patient, Specialty, Appointment, CenterConfig, ProfessionalSpecialty

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
        
        # ==================== CREAR ESPECIALIDADES ====================
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
        
        # ==================== HORARIOS POR ESPECIALIDAD ====================
        # Horario estándar para Psicología (lunes a viernes)
        horario_psicologia = {
            "monday": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "tuesday": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "wednesday": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "thursday": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "friday": {"enabled": True, "start": "09:00", "end": "18:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "saturday": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""},
            "sunday": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        # Horario para Psiquiatría (incluye sábado)
        horario_psiquiatria = {
            "monday": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "tuesday": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "wednesday": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "thursday": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "friday": {"enabled": True, "start": "10:00", "end": "17:00", "lunch_start": "13:00", "lunch_end": "14:00"},
            "saturday": {"enabled": True, "start": "09:00", "end": "13:00", "lunch_start": "", "lunch_end": ""},
            "sunday": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        # Horario para Terapias (tardes)
        horario_terapias = {
            "monday": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "tuesday": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "wednesday": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "thursday": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "friday": {"enabled": True, "start": "14:00", "end": "20:00", "lunch_start": "", "lunch_end": ""},
            "saturday": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""},
            "sunday": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        # Horario para Neuropsicología (mañanas)
        horario_neuropsicologia = {
            "monday": {"enabled": True, "start": "08:00", "end": "14:00", "lunch_start": "", "lunch_end": ""},
            "tuesday": {"enabled": True, "start": "08:00", "end": "14:00", "lunch_start": "", "lunch_end": ""},
            "wednesday": {"enabled": True, "start": "08:00", "end": "14:00", "lunch_start": "", "lunch_end": ""},
            "thursday": {"enabled": True, "start": "08:00", "end": "14:00", "lunch_start": "", "lunch_end": ""},
            "friday": {"enabled": True, "start": "08:00", "end": "14:00", "lunch_start": "", "lunch_end": ""},
            "saturday": {"enabled": True, "start": "09:00", "end": "12:00", "lunch_start": "", "lunch_end": ""},
            "sunday": {"enabled": False, "start": "", "end": "", "lunch_start": "", "lunch_end": ""}
        }
        
        # ==================== CREAR PROFESIONALES ====================
        profesionales = [
            # ADMIN - Sin especialidades ni horarios
            Professional(
                name='Administrador Centro',
                email='admin@cuad.cl',
                password_hash=generate_password_hash('1234'),
                role='admin',
                schedule={}  # Admin no tiene horarios
            ),
            
            # MEMBER 1 - Juan (Terapias) - CON TÉRMINOS
            Professional(
                name='Dr. Juan Pérez',
                email='juan@cuad.cl',
                password_hash=generate_password_hash('1234'),
                role='member',
                schedule={
                    str(especialidades[2].id): horario_terapias,
                    str(especialidades[3].id): horario_terapias,
                }
            ),
            
            # MEMBER 2 - Ana (Psicología) - CON TÉRMINOS
            Professional(
                name='Dra. Ana García',
                email='ana@cuad.cl',
                password_hash=generate_password_hash('1234'),
                role='member',
                schedule={
                    str(especialidades[0].id): horario_psicologia,
                }
            ),
            
            # LIMITED - Carlos (Psiquiatría) - SIN TÉRMINOS (para probar notificación)
            Professional(
                name='Dr. Carlos Rojas',
                email='carlos@cuad.cl',
                password_hash=generate_password_hash('1234'),
                role='limited',
                schedule={
                    str(especialidades[1].id): horario_psiquiatria,
                }
            ),
            
            # MEMBER 3 - Laura (Neuropsicología) - CON TÉRMINOS
            Professional(
                name='Dra. Laura Martínez',
                email='laura@cuad.cl',
                password_hash=generate_password_hash('1234'),
                role='member',
                schedule={
                    str(especialidades[4].id): horario_neuropsicologia,
                }
            ),
        ]
        
        for prof in profesionales:
            db.session.add(prof)
        db.session.commit()
        print(f"✓ {len(profesionales)} profesionales creados")
        
        # ==================== ASIGNAR ESPECIALIDADES CON TÉRMINOS ====================
        
        # Juan - Terapias (CON TÉRMINOS)
        juan_terapia_pareja = ProfessionalSpecialty(
            professional_id=profesionales[1].id,
            specialty_id=especialidades[2].id,
            terms_and_conditions="""TÉRMINOS Y CONDICIONES - TERAPIA DE PAREJA

1. ASISTENCIA Y PUNTUALIDAD
   - Las sesiones tienen una duración de 90 minutos.
   - Se requiere puntualidad. Después de 15 minutos de retraso, la sesión puede ser reagendada.
   - Ambos miembros de la pareja deben asistir salvo indicación contraria del terapeuta.

2. CANCELACIONES Y REAGENDAMIENTO
   - Las cancelaciones deben realizarse con al menos 48 horas de anticipación.
   - Cancelaciones tardías o inasistencias sin aviso serán cobradas al 100%.
   - Máximo 2 reagendamientos por mes.

3. CONFIDENCIALIDAD
   - Todo lo conversado en sesión es estrictamente confidencial.
   - La información solo puede compartirse con autorización explícita de ambas partes.

4. COMPROMISO TERAPÉUTICO
   - Se requiere compromiso de ambos miembros para el proceso terapéutico.
   - Pueden asignarse tareas o ejercicios entre sesiones.
   - El progreso depende de la participación activa de la pareja.

5. PAGOS
   - El pago debe realizarse al inicio de cada sesión.
   - Se aceptan efectivo, transferencia o tarjetas de crédito/débito.""",
            has_terms=True,
            is_active=True
        )
        
        juan_terapia_familiar = ProfessionalSpecialty(
            professional_id=profesionales[1].id,
            specialty_id=especialidades[3].id,  # Terapia Familiar
            terms_and_conditions="""TÉRMINOS Y CONDICIONES - TERAPIA FAMILIAR

1. SESIONES FAMILIARES
   - Duración: 90 minutos por sesión.
   - Se requiere la asistencia de todos los miembros indicados por el terapeuta.
   - Puntualidad obligatoria: 10 minutos de tolerancia máxima.

2. PARTICIPACIÓN
   - Todos los miembros deben participar activamente y respetuosamente.
   - Ambiente de respeto mutuo durante las sesiones.
   - Prohibido el uso de dispositivos móviles durante la sesión.

3. CANCELACIONES
   - Avisar con mínimo 48 horas de anticipación.
   - Máximo 2 cancelaciones por mes.
   - Inasistencias sin aviso: cobro del 100% de la sesión.

4. CONFIDENCIALIDAD Y PRIVACIDAD
   - La información compartida es confidencial.
   - Se respeta la privacidad de cada miembro de la familia.

5. PROCESO TERAPÉUTICO
   - Pueden asignarse tareas familiares entre sesiones.
   - El progreso requiere compromiso de todos los miembros.
   - Evaluaciones periódicas del avance terapéutico.""",
            has_terms=True,
            is_active=True
        )
        
        # Ana - Psicología (CON TÉRMINOS)
        ana_psicologia = ProfessionalSpecialty(
            professional_id=profesionales[2].id,
            specialty_id=especialidades[0].id,  # Psicología
            terms_and_conditions="""TÉRMINOS Y CONDICIONES - ATENCIÓN PSICOLÓGICA

1. DURACIÓN Y FORMATO DE SESIONES
   - Cada sesión tiene una duración de 60 minutos.
   - Las sesiones son individuales y confidenciales.
   - Se requiere llegar 5 minutos antes para registro.

2. ASISTENCIA Y PUNTUALIDAD
   - La puntualidad es fundamental para aprovechar el tiempo terapéutico.
   - Retrasos mayores a 10 minutos reducirán el tiempo de sesión.
   - Después de 20 minutos, la sesión se considerará perdida.

3. CANCELACIONES Y REAGENDAMIENTO
   - Cancelar con mínimo 24 horas de anticipación.
   - Primera cancelación sin cargo si se avisa con tiempo.
   - Cancelaciones reiteradas o sin aviso serán cobradas.
   - Reagendamiento disponible según disponibilidad.

4. PROCESO TERAPÉUTICO
   - La terapia es un proceso colaborativo entre paciente y terapeuta.
   - Se requiere honestidad y apertura para mejores resultados.
   - Pueden asignarse ejercicios o reflexiones entre sesiones.

5. CONFIDENCIALIDAD
   - Todo lo conversado es estrictamente confidencial.
   - Excepciones: riesgo inminente para sí mismo o terceros, o requerimiento judicial.

6. PAGOS Y FACTURACIÓN
   - Pago al inicio de cada sesión.
   - Bonos y convenios deben informarse previamente.
   - Emisión de boleta o factura según requerimiento.""",
            has_terms=True,
            is_active=True
        )
        
        # Carlos - Psiquiatría (SIN TÉRMINOS - para probar notificación)
        carlos_psiquiatria = ProfessionalSpecialty(
            professional_id=profesionales[3].id,
            specialty_id=especialidades[1].id,  # Psiquiatría
            terms_and_conditions=None,
            has_terms=False,
            is_active=False  # No está activo hasta que agregue términos
        )
        
        # Laura - Neuropsicología (CON TÉRMINOS)
        laura_neuropsicologia = ProfessionalSpecialty(
            professional_id=profesionales[4].id,
            specialty_id=especialidades[4].id,  # Neuropsicología
            terms_and_conditions="""TÉRMINOS Y CONDICIONES - EVALUACIÓN NEUROPSICOLÓGICA

1. EVALUACIONES Y PRUEBAS
   - Las evaluaciones neuropsicológicas requieren varias sesiones.
   - Duración aproximada: 3-5 sesiones de 60 minutos cada una.
   - Es fundamental completar todas las sesiones programadas.

2. PREPARACIÓN PARA LA EVALUACIÓN
   - Descansar adecuadamente la noche anterior.
   - Desayunar/almorzar antes de la sesión.
   - Traer lentes o audífonos si los usa habitualmente.
   - Evitar consumo de alcohol 24 horas antes.

3. ASISTENCIA
   - Reagendar con mínimo 48 horas de anticipación.
   - La inasistencia interrumpe el proceso de evaluación.
   - Puede requerirse reiniciar el proceso en caso de ausencias prolongadas.

4. INFORMES Y RESULTADOS
   - El informe final se entrega 15 días después de completar las evaluaciones.
   - Los resultados se explican en sesión de devolución.
   - El informe es confidencial y propiedad del paciente.

5. SEGUIMIENTO Y REHABILITACIÓN
   - Si se requiere rehabilitación, se programará según disponibilidad.
   - Las sesiones de rehabilitación tienen duración y frecuencia variable.

6. CONFIDENCIALIDAD
   - Toda la información obtenida es estrictamente confidencial.
   - Los informes solo se entregan al paciente o tutor legal.""",
            has_terms=True,
            is_active=True
        )
        
        # Agregar todas las asociaciones
        db.session.add(juan_terapia_pareja)
        db.session.add(juan_terapia_familiar)
        db.session.add(ana_psicologia)
        db.session.add(carlos_psiquiatria)
        db.session.add(laura_neuropsicologia)
        db.session.commit()
        print("✓ Especialidades asignadas con términos y condiciones")
        
        # ==================== CREAR PACIENTES ====================
        pacientes = [
            Patient(
                name='María López',
                email='maria.lopez@email.com',
                phone='+56912345678',
                rut='12345678-9',
                birth_date=datetime(1990, 5, 15).date()
            ),
            Patient(
                name='Pedro Sánchez',
                email='pedro.sanchez@email.com',
                phone='+56923456789',
                rut='23456789-0',
                birth_date=datetime(1985, 8, 20).date()
            ),
            Patient(
                name='Laura Fernández',
                email='laura.fernandez@email.com',
                phone='+56934567890',
                rut='34567890-1',
                birth_date=datetime(1992, 3, 10).date()
            ),
            Patient(
                name='Roberto Torres',
                email='roberto.torres@email.com',
                phone='+56945678901',
                rut='45678901-2',
                birth_date=datetime(1988, 11, 25).date()
            ),
            Patient(
                name='Sofía Ramírez',
                email='sofia.ramirez@email.com',
                phone='+56956789012',
                rut='56789012-3',
                birth_date=datetime(1995, 7, 8).date()
            ),
        ]
        
        for paciente in pacientes:
            db.session.add(paciente)
        db.session.commit()
        print(f"✓ {len(pacientes)} pacientes creados")
        
        # ==================== CREAR CITAS DE EJEMPLO ====================
        hoy = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
        
        citas = [
            # Citas confirmadas
            Appointment(
                patient_id=pacientes[0].id,
                professional_id=profesionales[1].id,  # Juan
                specialty_id=especialidades[2].id,    # Terapia de Pareja
                date=hoy,
                status='confirmed',
                notes='Terapia de pareja - Sesión 3. Trabajando en comunicación.'
            ),
            Appointment(
                patient_id=pacientes[1].id,
                professional_id=profesionales[2].id,  # Ana
                specialty_id=especialidades[0].id,    # Psicología
                date=hoy.replace(hour=10),
                status='confirmed',
                notes='Primera consulta. Motivo: ansiedad y estrés laboral.'
            ),
            Appointment(
                patient_id=pacientes[2].id,
                professional_id=profesionales[4].id,  # Laura
                specialty_id=especialidades[4].id,    # Neuropsicología
                date=hoy + timedelta(days=1, hours=-5),
                status='confirmed',
                notes='Evaluación neuropsicológica - Sesión 2 de 4.'
            ),
            
            # Citas pendientes
            Appointment(
                patient_id=pacientes[3].id,
                professional_id=profesionales[1].id,  # Juan
                specialty_id=especialidades[3].id,    # Terapia Familiar
                date=hoy + timedelta(days=2),
                status='pending',
                notes='Primera sesión familiar. Incluir a todos los miembros.'
            ),
            Appointment(
                patient_id=pacientes[4].id,
                professional_id=profesionales[2].id,  # Ana
                specialty_id=especialidades[0].id,    # Psicología
                date=hoy + timedelta(days=3, hours=-2),
                status='pending',
                notes='Seguimiento mensual de tratamiento.'
            ),
            
            # Cita completada
            Appointment(
                patient_id=pacientes[0].id,
                professional_id=profesionales[2].id,  # Ana
                specialty_id=especialidades[0].id,    # Psicología
                date=hoy - timedelta(days=7),
                status='pending',
                notes='Sesión de seguimiento completada exitosamente.'
            ),
        ]
        
        for cita in citas:
            db.session.add(cita)
        db.session.commit()
        print(f"✓ {len(citas)} citas creadas")
        
        # ==================== CONFIGURACIÓN DEL CENTRO ====================
        config = CenterConfig(
            name='Centro de Salud Cuad',
            vision='Brindar atención integral en salud mental, promoviendo el bienestar y la calidad de vida de nuestros pacientes a través de un enfoque humanista y profesional.',
            address='Av. Principal 123, Providencia, Santiago',
            phone='+56912345678',
            email='contacto@cuad.cl',
            description='Centro especializado en salud mental y bienestar psicológico con profesionales altamente calificados.'
        )
        db.session.add(config)
        db.session.commit()
        print("✓ Configuración del centro creada")
        
        # ==================== RESUMEN FINAL ====================
        print("\n" + "="*70)
        print("BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print(f"Base de datos: {'PostgreSQL (Aiven)' if DATABASE_URL else 'SQLite Local'}")
        print("="*70)


if __name__ == "__main__":
    init_database()