from controllers.login_controller import login
from controllers.dashboard_controller import get_appointments
from controllers.public_controller import get_available_hours
from controllers.public_controller import create_appointment

def register_routes(app):
    app.add_url_rule('/login', 'login', login, methods=['POST'])
    app.add_url_rule('/appointments', 'get_appointments', get_appointments, methods=['GET'])
    app.add_url_rule('/available-hours', 'get_available_hours', get_available_hours, methods=['GET'])
    app.add_url_rule('/create-appointment', 'create_appointment', create_appointment, methods=['POST'])