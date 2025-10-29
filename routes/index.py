from controllers.login_controller import login
from controllers.dashboard_controller import get_appointments
from controllers.public_controller import get_available_hours, create_appointment
from controllers.center_controller import get_center_config, update_center_config
from controllers.services_controller import (
    get_services, create_service, update_service, delete_service
)
from controllers.appointments_controller import (
    cancel_appointment, reschedule_appointment, get_all_appointments,
    create_appointment_admin, update_appointment_admin
)
from controllers.professional_controller import (
    get_professionals, get_professional, create_professional,
    update_professional, delete_professional, assign_specialties
)
from controllers.patient_controller import (
    get_patients, get_patient, create_patient,
    update_patient, delete_patient, search_patients
)

def register_routes(app):
    # =============== AUTH ===============
    app.add_url_rule('/api/login', 'login', login, methods=['POST'])
    
    # =============== DASHBOARD ===============
    app.add_url_rule('/api/appointments', 'get_appointments', get_appointments, methods=['GET'])
    app.add_url_rule('/api/appointments/all', 'get_all_appointments', get_all_appointments, methods=['GET'])
    
    # =============== PUBLIC (Agendamiento Público) ===============
    app.add_url_rule('/api/available-hours', 'get_available_hours', get_available_hours, methods=['GET'])
    app.add_url_rule('/api/create-appointment', 'create_appointment', create_appointment, methods=['POST'])
    
    # =============== CENTER CONFIG (Admin only) ===============
    app.add_url_rule('/api/center-config', 'get_center_config', get_center_config, methods=['GET'])
    app.add_url_rule('/api/center-config', 'update_center_config', update_center_config, methods=['PUT'])
    
    # =============== SERVICES (Admin only) ===============
    app.add_url_rule('/api/services', 'get_services', get_services, methods=['GET'])
    app.add_url_rule('/api/services', 'create_service', create_service, methods=['POST'])
    app.add_url_rule('/api/services/<int:service_id>', 'update_service', update_service, methods=['PUT'])
    app.add_url_rule('/api/services/<int:service_id>', 'delete_service', delete_service, methods=['DELETE'])
    
    # =============== APPOINTMENTS MANAGEMENT ===============
    app.add_url_rule('/api/appointments/create', 'create_appointment_admin', create_appointment_admin, methods=['POST'])
    app.add_url_rule('/api/appointments/<int:appointment_id>', 'update_appointment_admin', update_appointment_admin, methods=['PUT'])
    app.add_url_rule('/api/appointments/<int:appointment_id>/cancel', 'cancel_appointment', cancel_appointment, methods=['DELETE'])
    app.add_url_rule('/api/appointments/<int:appointment_id>/reschedule', 'reschedule_appointment', reschedule_appointment, methods=['PUT'])
    
    # =============== PROFESSIONALS (Admin only) ===============
    app.add_url_rule('/api/professionals', 'get_professionals', get_professionals, methods=['GET'])
    app.add_url_rule('/api/professionals/<int:professional_id>', 'get_professional', get_professional, methods=['GET'])
    app.add_url_rule('/api/professionals', 'create_professional', create_professional, methods=['POST'])
    app.add_url_rule('/api/professionals/<int:professional_id>', 'update_professional', update_professional, methods=['PUT'])
    app.add_url_rule('/api/professionals/<int:professional_id>', 'delete_professional', delete_professional, methods=['DELETE'])
    app.add_url_rule('/api/professionals/<int:professional_id>/specialties', 'assign_specialties', assign_specialties, methods=['PUT'])
    
    # =============== PATIENTS (Admin only) ===============
    app.add_url_rule('/api/patients', 'get_patients', get_patients, methods=['GET'])
    app.add_url_rule('/api/patients/<int:patient_id>', 'get_patient', get_patient, methods=['GET'])
    app.add_url_rule('/api/patients', 'create_patient', create_patient, methods=['POST'])
    app.add_url_rule('/api/patients/<int:patient_id>', 'update_patient', update_patient, methods=['PUT'])
    app.add_url_rule('/api/patients/<int:patient_id>', 'delete_patient', delete_patient, methods=['DELETE'])
    app.add_url_rule('/api/patients/search', 'search_patients', search_patients, methods=['GET'])