from data.db import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    rol = db.Column(db.String(50))  # administrador, miembro, limitado

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    duracion = db.Column(db.Integer)

class Agendamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    fecha = db.Column(db.String(50))
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id'))
    profesional_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))