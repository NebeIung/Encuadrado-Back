from flask import Blueprint, request, jsonify
from controllers.dashboard_controller import get_agendamientos

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard", methods=["POST"])
def dashboard_route():
    """Se espera que el frontend mande { id, rol } del usuario logueado"""
    data = request.get_json()
    return get_agendamientos(data)