from flask import Blueprint
from controllers.paciente_controller import get_datos_centro, crear_agendamiento

paciente_bp = Blueprint("paciente", __name__)

@paciente_bp.route("/centro", methods=["GET"])
def datos_centro():
    return get_datos_centro()

@paciente_bp.route("/agendar", methods=["POST"])
def agendar():
    return crear_agendamiento()