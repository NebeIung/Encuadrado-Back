from controllers.login_controller import login
from controllers.appointments_controller import (
    get_dashboard_stats,
    get_all_appointments,
    create_appointment_admin,
    update_appointment_admin,
    cancel_appointment,
    reschedule_appointment
)
from controllers.services_controller import (
    get_services, 
    create_service, 
    update_service, 
    delete_service
)
from controllers.patient_controller import get_patients, create_patient
from controllers.center_controller import get_center_config, update_center_config
from controllers.professional_controller import (
    get_professionals,
    get_professional,
    create_professional,
    update_professional,
    delete_professional,
    assign_specialties,
    update_professional_schedule,
    update_specialty_terms,
    get_pending_terms
)

def register_routes(app):
    # Login
    app.add_url_rule('/api/login', 'login', login, methods=['POST'])
    
    # Dashboard y Estadísticas
    app.add_url_rule('/api/appointments', 'get_dashboard_stats', get_dashboard_stats, methods=['GET'])
    
    # Appointments Management
    app.add_url_rule('/api/appointments/list', 'get_all_appointments', get_all_appointments, methods=['GET'])
    app.add_url_rule('/api/appointments', 'create_appointment_admin', create_appointment_admin, methods=['POST'])
    app.add_url_rule('/api/appointments/<int:appointment_id>', 'update_appointment_admin', update_appointment_admin, methods=['PUT'])
    app.add_url_rule('/api/appointments/<int:appointment_id>/cancel', 'cancel_appointment', cancel_appointment, methods=['PUT'])
    app.add_url_rule('/api/appointments/<int:appointment_id>/reschedule', 'reschedule_appointment', reschedule_appointment, methods=['PUT'])
    
    # Services (Especialidades)
    app.add_url_rule('/api/services', 'get_services', get_services, methods=['GET'])
    app.add_url_rule('/api/services', 'create_service', create_service, methods=['POST'])
    app.add_url_rule('/api/services/<int:service_id>', 'update_service', update_service, methods=['PUT'])
    app.add_url_rule('/api/services/<int:service_id>', 'delete_service', delete_service, methods=['DELETE'])
    
    # Patients
    app.add_url_rule('/api/patients', 'get_patients', get_patients, methods=['GET'])
    app.add_url_rule('/api/patients', 'create_patient', create_patient, methods=['POST'])
    
    # Center Config
    app.add_url_rule('/api/center-config', 'get_center_config', get_center_config, methods=['GET'])
    app.add_url_rule('/api/center-config', 'update_center_config', update_center_config, methods=['PUT'])
    
    # Professionals
    app.add_url_rule('/api/professionals', 'get_professionals', get_professionals, methods=['GET'])
    app.add_url_rule('/api/professionals/<int:professional_id>', 'get_professional', get_professional, methods=['GET'])
    app.add_url_rule('/api/professionals', 'create_professional', create_professional, methods=['POST'])
    app.add_url_rule('/api/professionals/<int:professional_id>', 'update_professional', update_professional, methods=['PUT'])
    app.add_url_rule('/api/professionals/<int:professional_id>', 'delete_professional', delete_professional, methods=['DELETE'])
    app.add_url_rule('/api/professionals/<int:professional_id>/specialties', 'assign_specialties', assign_specialties, methods=['PUT'])
    app.add_url_rule('/api/professionals/<int:professional_id>/schedule', 'update_professional_schedule', update_professional_schedule, methods=['PUT'])
    
    # Términos y Condiciones
    app.add_url_rule('/api/professionals/<int:professional_id>/pending-terms', 'get_pending_terms', get_pending_terms, methods=['GET'])
    app.add_url_rule('/api/professionals/<int:professional_id>/specialties/<int:specialty_id>/terms', 'update_specialty_terms', update_specialty_terms, methods=['PUT'])
    
    # Ruta especial para especialidades con profesionales
    app.add_url_rule('/api/specialties', 'get_specialties_with_professionals', get_services, methods=['GET'])