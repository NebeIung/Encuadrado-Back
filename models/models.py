from config.db_config import db
from datetime import datetime

# Tabla intermedia MEJORADA para especialidades con términos y condiciones
class ProfessionalSpecialty(db.Model):
    __tablename__ = 'professional_specialties'
    
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), primary_key=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), primary_key=True)
    terms_and_conditions = db.Column(db.Text, nullable=True)
    has_terms = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'professional_id': self.professional_id,
            'specialty_id': self.specialty_id,
            'terms_and_conditions': self.terms_and_conditions,
            'has_terms': self.has_terms,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')
    schedule = db.Column(db.JSON, nullable=True)
    
    # Relación directa con la tabla intermedia
    specialty_associations = db.relationship(
        'ProfessionalSpecialty',
        foreign_keys='ProfessionalSpecialty.professional_id',
        backref='professional_obj',
        cascade='all, delete-orphan'
    )
    
    specialties = db.relationship(
        'Specialty',
        secondary='professional_specialties',
        viewonly=True,
        overlaps="specialty_associations,professional_obj"
    )
    
    appointments = db.relationship('Appointment', backref='professional', lazy=True)
    
    def get_specialties_with_terms(self):
        """Obtener especialidades con información de términos"""
        result = []
        for assoc in self.specialty_associations:
            specialty = Specialty.query.get(assoc.specialty_id)
            if specialty:
                result.append({
                    'id': specialty.id,
                    'name': specialty.name,
                    'description': specialty.description or '',
                    'duration': specialty.duration,
                    'price': specialty.price,
                    'color': specialty.color or '#1976d2',
                    'has_terms': assoc.has_terms,
                    'is_active': assoc.is_active,
                    'terms_and_conditions': assoc.terms_and_conditions,
                    'updated_at': assoc.updated_at.isoformat() if assoc.updated_at else None,
                })
        return result
    
    def to_dict(self, include_terms=False):
        # El admin principal (admin@centro.com) no debe tener especialidades
        if self.email == 'admin@centro.com':
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'role': self.role,
                'schedule': {},
                'specialties': []
            }
        
        specialties_data = self.get_specialties_with_terms() if include_terms else [
            {
                'id': s.id,
                'name': s.name,
                'description': s.description or '',
                'duration': s.duration,
                'price': s.price,
                'color': s.color or '#1976d2'
            } for s in self.specialties
        ]
        
        # Verificar si hay especialidades sin términos
        pending_terms = []
        if include_terms:
            pending_terms = [s for s in specialties_data if not s['has_terms']]
        
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'schedule': self.schedule or {},
            'specialties': specialties_data,
            'has_pending_terms': len(pending_terms) > 0 if include_terms else False,
            'pending_terms_count': len(pending_terms) if include_terms else 0,
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    
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
    
    # Relación simplificada
    professionals = db.relationship(
        'Professional',
        secondary='professional_specialties',
        viewonly=True,
        overlaps="professional_obj,specialty_associations"
    )
    
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
            # Excluir admin@centro.com y solo contar profesionales CON términos activos
            active_professionals = []
            for assoc in ProfessionalSpecialty.query.filter_by(specialty_id=self.id).all():
                prof = Professional.query.get(assoc.professional_id)
                if prof and prof.email != 'admin@centro.com' and assoc.has_terms and assoc.is_active:
                    active_professionals.append({
                        'id': prof.id,
                        'name': prof.name,
                        'has_terms': assoc.has_terms,
                    })
            
            result['professionals_count'] = len(active_professionals)
            result['professionals'] = active_professionals
        
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
    name = db.Column(db.String(200), nullable=False, default='Centro de Salud')
    address = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    description = db.Column(db.Text)
    vision = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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