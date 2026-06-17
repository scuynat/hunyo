from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager
import os
import requests
import time

app = Flask(__name__)

SECRET = os.environ["SECRET"]

counter = 0

last_failed_lock = 0

already_locked_count = 0
already_locked_window_start = 0

disabled = False

@app.route("/")
def root():
    return "OK"

@app.route("/disable")
def disable():
    global disabled
    
    if request.args.get("secret") != SECRET:
        return "Forbidden", 403
    
    disabled = True
    return "Disabled OK at " + str(time.time())

@app.route("/enable")
def enable():
    global disabled
    
    if request.args.get("secret") != SECRET:
        return "Forbidden", 403
    
    disabled = False
    return "Enabled OK at " + str(time.time())

@app.route("/test")
def test():
    global counter
    counter += 1
    return str(counter)

@app.route("/lock")
def lock():
    global last_failed_lock
    global already_locked_count
    global already_locked_window_start
    global disabled
    if request.args.get("secret") != SECRET:
        return "Forbidden", 403

    if disabled:
        return "Service disabled", 403
    
    try: 
        vm = VehicleManager(
            region=1,                 # Europe
            brand=2,                  # Hyundai
            username=os.environ["HYUNDAI_USER"],
            password=os.environ["HYUNDAI_PASS"],
            pin=os.environ["HYUNDAI_PIN"]
        )
    
        vm.check_and_refresh_token()
        vm.force_refresh_all_vehicles_states()
        vm.update_all_vehicles_with_cached_state()          
        vehicle = next(iter(vm.vehicles.values()))
        s = vehicle.data["vehicleStatus"]

        now = time.time()
        
        if s["doorLock"]:

            if (
                already_locked_window_start == 0
                or now - already_locked_window_start > 300
            ):
                already_locked_window_start = now
                already_locked_count = 1
            else:
                already_locked_count += 1
            
            if already_locked_count >= 3:

                requests.post(
                    "https://api.pushover.net/1/messages.json",
                    data={
                        "token": os.environ["PUSHOVER_API_TOKEN"],
                        "user": os.environ["PUSHOVER_USER_KEY"],
                        "message": "5 percen belül legalább 3 zárási kísérlet történt úgy, hogy az autó már zárva volt. Lehet, hogy rossz helyen van a kulcs!"
                    }
                )

                already_locked_count = 0
                already_locked_window_start = now

                return "Már zárva 3x, push elküldve"

            return "Már zárva"

        if (
                s["doorOpen"]["frontLeft"] == 1
                or s["doorOpen"]["frontRight"] == 1
                or s["doorOpen"]["backLeft"] == 1
                or s["doorOpen"]["backRight"] == 1
                or s["trunkOpen"]
                or s["engine"]
        ):
            last_failed_lock = now
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": os.environ["PUSHOVER_API_TOKEN"],
                    "user": os.environ["PUSHOVER_USER_KEY"],
                    "message": "Nem sikerült a zárás, mert nyitva valamelyik ajtó, vagy READY-ben van az autó"
                }
            )

            return "Nem sikerült a zárás, push elküldve"

        vm.lock(vehicle.id)

        if last_failed_lock != 0 and now - last_failed_lock <= 120:

            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": os.environ["PUSHOVER_API_TOKEN"],
                    "user": os.environ["PUSHOVER_USER_KEY"],
                    "message": "Korábban nem sikerült a zárás (ajtó nyitva vagy READY állapot), de most sikeresen elküldtem a zárási parancsot."
                }
            )

            last_failed_lock = 0
            
            return "Zárás elindítva nyitott ajtó után, push elküldve"

        return "Zárás elindítva"
        
    except Exception as e:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.environ["PUSHOVER_API_TOKEN"],
                "user": os.environ["PUSHOVER_USER_KEY"],
                "message": "Hiba: " + str(e)
            }
        )
        return "Hiba: " + str(e) + ", push elküldve", 500


    
