from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager
import os
import inspect

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

    vm.check_and_refresh_token()
    #return "<br>".join(dir(vm))
    return str(inspect.signature(vm.lock))
    
    vm.force_refresh_all_vehicles_states()
    vm.update_all_vehicles_with_cached_state()

    try:
        vehicle = next(iter(vm.vehicles.values()))
        s = vehicle.data["vehicleStatus"]

        return jsonify({
            "locked": s["doorLock"],
            "engine": s["engine"],
            "frontLeft": s["doorOpen"]["frontLeft"],
            "frontRight": s["doorOpen"]["frontRight"],
            "backLeft": s["doorOpen"]["backLeft"],
            "backRight": s["doorOpen"]["backRight"],
            "trunkOpen": s["trunkOpen"]
        })
        
    except Exception as e:
        return str(e), 500


    
