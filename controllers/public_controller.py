from flask import jsonify, request
from data import professionals, services, appointments
from datetime import datetime, timedelta

def get_available_hours():
    date = request.args.get("date")  # YYYY-MM-DD
    professional_id = int(request.args.get("professionalId"))
    service_id = int(request.args.get("serviceId"))

    prof = next(p for p in professionals if p["id"] == professional_id)
    service = next(s for s in services if s["id"] == service_id)

    weekday = datetime.strptime(date, "%Y-%m-%d").weekday()
    keys = ["mon","tue","wed","thu","fri","sat","sun"]
    workblocks = prof["schedule"].get(keys[weekday], [])

    if not workblocks:
        return jsonify([])

    # Duración del servicio (min)
    duration = service["duration"]
    available = []

    for block in workblocks:
        start, end = block.split("-")
        current = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M")

        while current + timedelta(minutes=duration) <= end_time:
            time_str = current.strftime("%H:%M")
            # Validar que no choque con citas existentes
            booked = any(
                a["professionId"] == professional_id and
                a["date"].startswith(date) and
                a["date"].endswith(time_str)
                for a in appointments
            )
            if not booked:
                available.append(time_str)
            current += timedelta(minutes=duration)

    return jsonify(available)

def create_appointment():
    data = request.get_json()
    appointments.append(data)
    return jsonify({"message": "ok"}), 200