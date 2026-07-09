"""
routes.py - All API endpoints for the Delivery Route Optimizer.
This is the file to point to when someone asks "where's your API code?"
"""

import requests
from flask import Blueprint, request, jsonify, render_template

from db import get_db, build_graph, get_route_id, get_avg_delay, get_all_city_names
from route_engine_loader import find_shortest_path, USING_CPP

DELAY_THRESHOLD_MIN = 20          # if predicted delay > this, trigger alert
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/delay-alert"

# Blueprint groups all these routes together and gets registered on the app in app.py
api = Blueprint("api", __name__)


@api.route("/")
def index():
    return render_template("index.html")


@api.route("/api/cities", methods=["GET"])
def get_cities():
    """Returns all delivery points (cities) for populating the frontend dropdowns."""
    db = get_db()
    rows = db.execute("SELECT id, name, latitude, longitude FROM delivery_points").fetchall()
    return jsonify([dict(r) for r in rows])


@api.route("/api/find-route", methods=["POST"])
def find_route():
    """
    Main endpoint: takes {source, destination}, returns shortest path,
    total time, predicted delay, and triggers n8n alert if delay is high.
    """
    data = request.get_json()
    source_name = data.get("source")
    destination_name = data.get("destination")

    db = get_db()

    source_row = db.execute(
        "SELECT id FROM delivery_points WHERE name = ?", (source_name,)
    ).fetchone()
    dest_row = db.execute(
        "SELECT id FROM delivery_points WHERE name = ?", (destination_name,)
    ).fetchone()

    if not source_row or not dest_row:
        return jsonify({"error": "Invalid source or destination"}), 400

    source_id, dest_id = source_row["id"], dest_row["id"]

    # 1. Build graph & run Dijkstra (C++ engine, or Python fallback)
    graph = build_graph(db)
    result = find_shortest_path(graph, source_id, dest_id)

    if not result["found"]:
        return jsonify({"error": "No route exists between these points"}), 404

    path_ids = result["path"]
    total_time = result["total_time"]

    id_to_name = get_all_city_names(db)
    path_names = [id_to_name[i] for i in path_ids]

    # 2. Sum historical average delay across every edge in the path
    total_predicted_delay = 0.0
    for i in range(len(path_ids) - 1):
        route_id = get_route_id(db, path_ids[i], path_ids[i + 1])
        if route_id:
            total_predicted_delay += get_avg_delay(db, route_id)

    # 3. Check threshold -> trigger n8n if needed
    alert_status = "none"
    if total_predicted_delay > DELAY_THRESHOLD_MIN:
        alert_status = trigger_n8n_alert(db, path_names, total_predicted_delay, path_ids)

    return jsonify({
        "path": path_names,
        "total_time_min": total_time,
        "predicted_delay_min": round(total_predicted_delay, 1),
        "delay_risk": total_predicted_delay > DELAY_THRESHOLD_MIN,
        "alert_status": alert_status,
        "engine": "C++ (pybind11)" if USING_CPP else "Python (fallback)",
    })


def trigger_n8n_alert(db, path_names, predicted_delay, path_ids):
    """Calls the n8n webhook (external automation) and logs the alert in SQL."""
    payload = {
        "route": " -> ".join(path_names),
        "predicted_delay_min": round(predicted_delay, 1),
        "threshold": DELAY_THRESHOLD_MIN,
    }
    status = "logged"
    try:
        resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=3)
        if resp.ok:
            status = "sent"
    except requests.exceptions.RequestException:
        status = "n8n_unreachable"  # n8n not running - alert still logged in SQL below

    first_route_id = get_route_id(db, path_ids[0], path_ids[1]) if len(path_ids) > 1 else None
    if first_route_id:
        db.execute(
            "INSERT INTO alerts (route_id, predicted_delay, status) VALUES (?, ?, ?)",
            (first_route_id, predicted_delay, status),
        )
        db.commit()

    return status