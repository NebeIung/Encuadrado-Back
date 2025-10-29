professionals = [
    {
        "id": 1,
        "name": "admin",
        "email": "admin@centro.com",
        "role": "admin",
        "schedule": {
            "mon": ["09:00-13:00"],
            "tue": [],
            "wed": ["14:00-18:00"],
            "thu": [],
            "fri": ["09:00-18:00"],
        }
    },
    {
        "id": 2,
        "name": "juan",
        "email": "juan@centro.com",
        "role": "member",
        "schedule": {
            "mon": ["14:00-18:00"],
            "tue": ["09:00-13:00"],
            "wed": [],
            "thu": ["09:00-13:00"],
            "fri": [],
        }
    },
    {
        "id": 3,
        "name": "ana",
        "email": "ana@centro.com",
        "role": "limited",
        "schedule": {
            "mon": [],
            "tue": ["09:00-18:00"],
            "wed": ["14:00-18:00"],
            "thu": [],
            "fri": ["09:00-18:00"],
        }
    },
]

services = [
    {"id": 1, "name": "Consulta General", "duration": 30, "price": 25000},
    {"id": 2, "name": "Nutrición", "duration": 45, "price": 35000},
    {"id": 3, "name": "Psicología", "duration": 60, "price": 40000},
]

appointments = [
    {
        "id": 1, 
        "patient": "Diego Pérez", 
        "serviceId": 1, 
        "professionId": 2,
        "professionalEmail": "juan@centro.com",
        "date": "2025-10-30 10:00"
    },
    {
        "id": 2, 
        "patient": "María Torres", 
        "serviceId": 3, 
        "professionId": 3,
        "professionalEmail": "ana@centro.com",
        "date": "2025-10-31 15:00"
    },
    {
        "id": 3, 
        "patient": "Claudia Soto", 
        "serviceId": 2, 
        "professionId": 1,
        "professionalEmail": "admin@centro.com",
        "date": "2025-10-29 11:00"
    },
]