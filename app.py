from flask import Flask, request

app = Flask(__name__)

SECRET = "12346782343241236328723756"

@app.route("/")
def hello():
    return "OK"

@app.route("/lock")
def lock():
    if request.args.get("secret") != SECRET:
        return "Forbidden", 403

    return "Lock request received"
    
