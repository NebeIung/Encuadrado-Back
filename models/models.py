from config.db_config import db
from datetime import datetime

# Tabla intermedia para la relación muchos a muchos entre profesionales y especialidades
professional_specialties = db.Table('professional_specialties',
    db.Column('professional_id', db.Integer, db.ForeignKey('professionals.id'), primary_key=True),
    db.Column('specialty_id', db.Integer, db.ForeignKey('specialties.id'), primary_key=True)
)

class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')
    schedule = db.Column(db.JSON, nullable=True)
    
    # Relaciones
    specialties = db.relationship('Specialty', secondary=professional_specialties, backref='professionals')
    appointments = db.relationship('Appointment', backref='professional', lazy=True)
    
    def to_dict(self):
        # Admin no debe tener especialidades
        if self.role == 'admin':
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'role': self.role,
                'schedule': {},
                'specialties': []
            }
        
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'schedule': self.schedule or {},
            'specialties': [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description or '',
                    'duration': s.duration,
                    'price': s.price,
                    'color': s.color or '#1976d2'
                } for s in self.specialties
            ]
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    
    # Relaciones
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'rut': self.rut,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None
        }

class Specialty(db.Model):
    __tablename__ = 'specialties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#1976d2')
    
    # Relaciones
    appointments = db.relationship('Appointment', backref='specialty', lazy=True)
    
    def to_dict(self, include_professionals=False):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'duration': self.duration,
            'price': self.price,
            'color': self.color or '#1976d2'
        }
        
        if include_professionals:
            # Excluir admins del conteo
            non_admin_professionals = [p for p in self.professionals if p.role != 'admin']
            result['professionals_count'] = len(non_admin_professionals)
            result['professionals'] = [
                {'id': p.id, 'name': p.name} 
                for p in non_admin_professionals
            ]
        
        return result

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text, nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict() if self.patient else None,
            'professional': {
                'id': self.professional.id,
                'name': self.professional.name,
                'email': self.professional.email
            } if self.professional else None,
            'specialty': self.specialty.to_dict() if self.specialty else None,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'notes': self.notes,
            'cancellation_reason': self.cancellation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CenterConfig(db.Model):
    __tablename__ = 'center_config'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'description': self.description,
            'logo_url': self.logo_url
        }