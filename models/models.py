from config.db_config import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

# Tabla intermedia para relación muchos a muchos
professional_specialties = db.Table(
    "professional_specialties",
    db.Column("professional_id", db.Integer, db.ForeignKey("professionals.id"), primary_key=True),
    db.Column("specialty_id", db.Integer, db.ForeignKey("specialties.id"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow)
)

class Professional(db.Model):
    __tablename__ = "professionals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False, default="1234")
    role = db.Column(db.String(20), default="member")  # admin, member, limited
    phone = db.Column(db.String(20))
    schedule = db.Column(JSON)  # Horarios por día de la semana
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    specialties = db.relationship(
        'Specialty', 
        secondary=professional_specialties, 
        backref=db.backref('professionals', lazy='dynamic')
    )
    
    appointments = db.relationship(
        "Appointment", 
        backref="professional", 
        lazy="dynamic",
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
            "specialties": [s.to_dict_simple() for s in self.specialties],
            "created_at": self.created_at.isoformat() if self.created_at else None
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointments = db.relationship(
        "Appointment", 
        backref="patient", 
        lazy="dynamic",
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
            "rut": self.rut,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "emergency_phone": self.emergency_phone,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Specialty(db.Model):
    __tablename__ = "specialties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False, default=30)
    price = db.Column(db.Integer, nullable=False, default=0)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointments = db.relationship(
        "Appointment", 
        backref="specialty", 
        lazy="dynamic",
        foreign_keys="Appointment.specialty_id"
    )

    def __repr__(self):
        return f"<Specialty {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "price": self.price,
            "is_active": self.is_active,
            "professionals_count": self.professionals.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_simple(self):
        """Version sin professionals_count para evitar recursión"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "price": self.price,
            "is_active": self.is_active
        }


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professionals.id"), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey("specialties.id"), nullable=False)

    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="confirmed")  # confirmed, cancelled, completed, rescheduled
    notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment {self.id} - {self.date}>"

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.to_dict() if self.patient else None,
            "professional": {
                "id": self.professional.id,
                "name": self.professional.name,
                "email": self.professional.email
            } if self.professional else None,
            "specialty": self.specialty.to_dict_simple() if self.specialty else None,
            "date": self.date.isoformat() if self.date else None,
            "status": self.status,
            "notes": self.notes,
            "cancellation_reason": self.cancellation_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CenterConfig(db.Model):
    __tablename__ = "center_config"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    open_time = db.Column(db.String(5), default='09:00')  # HH:MM
    close_time = db.Column(db.String(5), default='18:00')  # HH:MM
    logo_url = db.Column(db.String(500))
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
            'openTime': self.open_time,
            'closeTime': self.close_time,
            'logo_url': self.logo_url,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }