"""
db.py - Database connection and helper functions.
Kept separate from routes.py so DB logic isn't mixed with API logic.
"""

import sqlite3
from flask import g

DATABASE = "route_optimizer.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def build_graph(db):
    """Builds adjacency list: {node_id: [(neighbor_id, time_weight), ...]}"""
    rows = db.execute(
        "SELECT source_id, destination_id, avg_time_min FROM routes"
    ).fetchall()
    graph = {}
    for r in rows:
        graph.setdefault(r["source_id"], []).append((r["destination_id"], r["avg_time_min"]))
    return graph


def get_route_id(db, node_a, node_b):
    """Finds the routes.id for a direct edge between two node ids (for delay lookup)."""
    row = db.execute(
        "SELECT id FROM routes WHERE source_id = ? AND destination_id = ?",
        (node_a, node_b),
    ).fetchone()
    return row["id"] if row else None


def get_avg_delay(db, route_id):
    row = db.execute(
        "SELECT AVG(actual_delay_min) as avg_delay FROM delay_history WHERE route_id = ?",
        (route_id,),
    ).fetchone()
    return row["avg_delay"] if row and row["avg_delay"] is not None else 0.0


def get_all_city_names(db):
    return {
        r["id"]: r["name"]
        for r in db.execute("SELECT id, name FROM delivery_points").fetchall()
    }
