from models.models import Professional, Specialty, Patient, Appointment
from config.db_config import db
from app import app

def seed_database():
    with app.app_context():

        # Limpieza previa
        db.drop_all()
        db.create_all()

        # ==== Profesionales ====
        admin = Professional(
            name="Isidora Azolas",
            email="admin@encuadrado.com",
            password="1234",
            role="admin",
            phone="+56911112222",
            schedule={
                "monday": ["09:00", "18:00"],
                "tuesday": ["09:00", "18:00"],
                "wednesday": ["09:00", "18:00"],
                "thursday": ["09:00", "18:00"],
                "friday": ["09:00", "16:00"]
            }
        )

        professional2 = Professional(
            name="Nicolás Pérez",
            email="nico@encuadrado.com",
            password="1234",
            role="member",
            phone="+56977778888",
            schedule={
                "monday": ["10:00", "16:00"],
                "tuesday": ["10:00", "16:00"],
                "thursday": ["14:00", "19:00"]
            }
        )

        # ==== Especialidades ====
        psicologia = Specialty(
            name="Sesión Psicológica",
            description="Atención psicológica individual",
            duration=50,
            price=35000
        )

        nutricion = Specialty(
            name="Consulta Nutricional",
            description="Evaluación nutricional y plan",
            duration=45,
            price=30000
        )

        terapia_pareja = Specialty(
            name="Terapia de Pareja",
            description="Sesión conjunta para parejas",
            duration=60,
            price=50000
        )

        # Asignar servicios a profesionales
        admin.specialties.append(psicologia)
        admin.specialties.append(terapia_pareja)
        professional2.specialties.append(nutricion)
        professional2.specialties.append(psicologia)

        # Guardar profesionales y especialidades
        db.session.add_all([admin, professional2, psicologia, nutricion, terapia_pareja])
        db.session.commit()

        # ==== Pacientes (mock) ====
        patient1 = Patient(
            name="Juan López",
            email="juan@example.com",
            phone="+56955556666"
        )
        db.session.add(patient1)
        db.session.commit()

        # ==== Cita de demo ====
        appointment = Appointment(
            patient_id=patient1.id,
            professional_id=admin.id,
            specialty_id=psicologia.id,
            date=datetime.utcnow() + timedelta(days=1, hours=2)  # mañana
        )
        db.session.add(appointment)
        db.session.commit()

        print("✅ Base de datos inicializada con éxito 🚀")


if __name__ == "__main__":
    seed_database()