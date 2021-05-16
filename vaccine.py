from datetime import date, datetime
from playsound import playsound
import requests
import json


URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
DISTRICT_ID = 307


def get_date():
    # To get current date
    today = date.today()
    today_date = str(today.strftime("%d/%m/%Y"))
    return today_date


def get_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def alert_with_sound():
    for i in range(2):
        playsound('alert.mp3')


def get_header_json():
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "cdn-api.co-vin.in",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    return header


def get_vaccine_status():
    params = {'district_id': DISTRICT_ID, 'date': get_date()}
    header = get_header_json()
    response = requests.get(url=URL, params=params, headers=header)
    return response.text


def get_available_sessions(sessions):
    available_sessions = []
    for session in sessions:
        session = dict(session)
        dose1_available_numbers = int(session.get("available_capacity_dose1"))
        dose2_available_numbers = int(session.get("available_capacity_dose2"))
        if dose1_available_numbers > 0 or dose2_available_numbers > 0:
            session.put("time", get_time())
            available_sessions.add(session)
    return available_sessions


def check_availability(response):
    response = json.loads(response)
    centers = list(response["centers"])
    output = dict()
    output["is_available"] = False
    for center in centers:
        center = dict(center)
        sessions = center["sessions"]
        available_sessions = list(get_available_sessions(sessions))
        if available_sessions:
            output["is_available"] = True
            output["available_sessions"] = available_sessions
            return output
    return output


def keep_checking_and_alert_if_found():
    while True:
        output_from_api = get_vaccine_status()
        availability = check_availability(output_from_api)
        is_available = availability["is_available"]
        if is_available:
            print(availability["available_sessions"])
            alert_with_sound()


if __name__ == '__main__':
    print("Start")
    keep_checking_and_alert_if_found()
    print("Stop")
