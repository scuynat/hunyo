from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager
import os
import inspect
import requests

app = Flask(__name__)

SECRET = os.environ["SECRET"]

@app.route("/")
def root():
    return "OK"

@app.route("/lock")
def lock():
    if request.args.get("secret") != SECRET:
        return "Forbidden", 403

    vm = VehicleManager(
        region=1,                 # Europe
        brand=2,                  # Hyundai
        username=os.environ["HYUNDAI_USER"],
        password=os.environ["HYUNDAI_PASS"],
        pin=os.environ["HYUNDAI_PIN"]
    )

    #vm.check_and_refresh_token()
    #vm.force_refresh_all_vehicles_states()
    #vm.update_all_vehicles_with_cached_state()

    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.environ["PUSHOVER_API_TOKEN"],
                "user": os.environ["PUSHOVER_USER_KEY"],
                "message": "heló"
            }
        )

        return "hihi"


        
        vehicle = next(iter(vm.vehicles.values()))
        s = vehicle.data["vehicleStatus"]

        if s["doorLock"]:
            return "Már zárva"

        if (
                s["doorOpen"]["frontLeft"] == 1
                or s["doorOpen"]["frontRight"] == 1
                or s["doorOpen"]["backLeft"] == 1
                or s["doorOpen"]["backRight"] == 1
                or s["trunkOpen"]
                or s["engine"]
        ):
            return "Nem sikerült a zárás, mert nyitva valamelyik ajtó, vagy READY-ben van az autó"

        vm.lock(vehicle.id)

        return "Zárás elindítva"
        
    except Exception as e:
        return str(e), 500


    
