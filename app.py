from flask import Flask, request, jsonify
from hyundai_kia_connect_api import VehicleManager
import os

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
    result = vm.force_refresh_all_vehicles_states()
    return str(result)
    


    
