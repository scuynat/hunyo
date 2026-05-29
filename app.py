from flask import Flask, request
import os

app = Flask(__name__)

SECRET = "12346782343241236328723756"

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
        pin=""
    )

    vm.check_and_refresh_token()
    vm.update_all_vehicles_with_cached_state()

    return str(vm.vehicles)
    
