from datetime import date, datetime
from playsound import playsound
from random import randint
from time import sleep
import requests
import json


URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
DISTRICT_ID = 307
MIN_DELAY_TIME = 0
MAX_DELAY_TIME = 6
FAILED_STATE = 2
SUCCESS_STATE = 1
NUM_CONSECUTIVE_FAILED_CASES_TO_ALERT = 20
NUM_FAILED_CASES_TO_DISPLAY = 30


def get_date():
    # To get current date
    today = date.today()
    today_date = str(today.strftime("%d/%m/%Y"))
    return today_date


def get_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def get_delay_time():
    n = randint(MIN_DELAY_TIME, MAX_DELAY_TIME*10)
    n /= 10
    return n


def alert_with_sound(case):
    if case == SUCCESS_STATE:
        audio = "alert.mp3"
    elif case == FAILED_STATE:
        audio = "failed_alert.mp3"
    for i in range(2):
        playsound(audio)


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


def is_failed_attempt(response):
    if response is None:
        return True
    if response.status_code != 200:
        return True
    return False
    

def get_vaccine_status():
    response = None
    try:
        params = {'district_id': DISTRICT_ID, 'date': get_date()}
        header = get_header_json()
        response = requests.get(url=URL, params=params, headers=header)
    except requests.exceptions.ConnectionError as errc:
        print("Network Error: Please check your network. Request retry initiated.")
    except requests.exceptions.Timeout as errt:
        print("Connection Timed out. Request retry initiated.")
    return response


def get_available_sessions(sessions):
    available_sessions = []
    for session in sessions:
        session = dict(session)
        dose1_available_numbers = int(session.get("available_capacity_dose1"))
        dose2_available_numbers = int(session.get("available_capacity_dose2"))
        if dose1_available_numbers > 0 or dose2_available_numbers > 0:
            print("Found a slot!!")
            session["time"] = get_time()
            available_sessions.append(session)
    return available_sessions


def check_availability(response):
    output = dict()
    output["is_available"] = False
    response = json.loads(response)
    centers = list(response["centers"])
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
    num_attempts = 0
    num_failed_attempts = 0
    consecutive_failed_attempt_count = 0
    while True:
        sleep(get_delay_time())
        output_from_api = get_vaccine_status()
        if is_failed_attempt(output_from_api):
            print("Failed Attempt")
            num_failed_attempts += 1
            if num_failed_attempts % NUM_FAILED_CASES_TO_DISPLAY == 0:
                print("Number of failed Attempts: " + str(num_failed_attempts))
            consecutive_failed_attempt_count += 1
            if consecutive_failed_attempt_count > NUM_CONSECUTIVE_FAILED_CASES_TO_ALERT:
                alert_with_sound(FAILED_STATE)
                consecutive_failed_attempt_count = 0
            continue
        else:
            consecutive_failed_attempt_count = 0
        num_attempts += 1
        print("Attempt: " + str(num_attempts))
        availability = check_availability(output_from_api.text)
        is_available = availability["is_available"]
        if is_available:
            print(availability["available_sessions"])
            alert_with_sound(SUCCESS_STATE)


if __name__ == '__main__':
    print("Start")
    keep_checking_and_alert_if_found()
    print("Stop")
