from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabla intermedia para relación muchos a muchos
professional_specialties = db.Table(
    "professional_specialties",
    db.Column("professional_id", db.Integer, db.ForeignKey("professionals.id"), primary_key=True),
    db.Column("specialty_id", db.Integer, db.ForeignKey("specialties.id"), primary_key=True),
    db.Column("created_at", db.DateTime(timezone=True), server_default=db.func.now())
)
class Professional(db.Model):
    __tablename__ = "professionals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False, default="1234")
    role = db.Column(db.String(20), default="member")  # admin, member, limited
    phone = db.Column(db.String(20))
    specialties = db.relationship('Specialty', secondary=professional_specialties, backref='professionals')

    appointments = db.relationship(
        "Appointment", backref="professional", lazy="dynamic",
        foreign_keys="Appointment.professional_id"
    )

    def __repr__(self):
        return f"<Professional {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "schedule": self.schedule,
            "is_active": self.is_active,
            "specialties": [s.to_dict(include_prof_count=False) for s in self.specialties],
        }

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    rut = db.Column(db.String(12), unique=True)
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(200))
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    appointments = db.relationship(
        "Appointment", backref="patient", lazy="dynamic",
        foreign_keys="Appointment.patient_id"
    )

    def __repr__(self):
        return f"<Patient {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }

class Specialty(db.Model):
    __tablename__ = "specialties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False, default=30)
    price = db.Column(db.Integer, nullable=False, default=0)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    appointments = db.relationship(
        "Appointment", backref="specialty", lazy="dynamic",
        foreign_keys="Appointment.specialty_id"
    )

    def __repr__(self):
        return f"<Specialty {self.name}>"

    def to_dict(self, include_prof_count=True):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "price": self.price,
            "is_active": self.is_active,
            **({"professionals_count": self.professionals.count()} if include_prof_count else {})
        }

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professionals.id"), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey("specialties.id"), nullable=False)

    date = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(20), default="confirmed")
    notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def __repr__(self):
        return f"<Appointment {self.id} - {self.date}>"

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.to_dict(),
            "professional": self.professional.to_dict(),
            "specialty": self.specialty.to_dict(),
            "date": self.date.isoformat(),
            "status": self.status,
            "notes": self.notes,
        }

class CenterConfig(db.Model):
    __tablename__ = "center_config"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    open_time = db.Column(db.String(5))
    close_time = db.Column(db.String(5))
    logo_url = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CenterConfig {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'open_time': self.open_time,
            'close_time': self.close_time,
            'logo_url': self.logo_url,
            'updated_at': self.updated_at
        }
