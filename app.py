from flask import Flask, jsonify, request

from duckfine import DuckFine

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/fine")
def fine():
    days = request.args.get("days", type=int)
    deluxe = request.args.get("deluxe", "0") in ("1", "true")
    if days is None:
        return jsonify(error="days must be a whole number"), 400
    try:
        fee = DuckFine("quote").charge(days, deluxe=deluxe)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(days_late=days, deluxe=deluxe, fee=fee)


