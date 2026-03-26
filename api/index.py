"""Flask API as Vercel Python function (`/api/index`); static UI lives in `public/`."""

import os
import urllib.parse
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

todos = []
_next_id = 1


@app.get("/api/todos")
def list_todos():
    return jsonify(todos)


@app.post("/api/todos")
def add_todo():
    global _next_id
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    item = {"id": _next_id, "text": text, "done": False}
    _next_id += 1
    todos.append(item)
    return jsonify(item), 201


@app.patch("/api/todos/<int:todo_id>")
def toggle_todo(todo_id):
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = not t["done"]
            return jsonify(t)
    return jsonify({"error": "not found"}), 404


@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id):
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            todos.pop(i)
            return jsonify({"ok": True}), 200
    return jsonify({"error": "not found"}), 404


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(STATIC_DIR, "assets"), filename)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    return send_from_directory(STATIC_DIR, "index.html")


def _vercel_path_fix(wsgi_app):
    """Restore original PATH_INFO when Vercel's rewrite overwrites it with the destination.

    Vercel sets PATH_INFO to the rewrite *destination* (/api/index) rather than
    the original request path.  It also sends the captured route parameters in
    the x-now-route-matches header (e.g. "path=api%2Ftodos" for named captures
    or "1=api%2Ftodos" for positional captures), which lets us reconstruct the
    real path before Flask does its URL matching.
    """
    def application(environ, start_response):
        if environ.get("PATH_INFO") == "/api/index":
            raw = environ.get("HTTP_X_NOW_ROUTE_MATCHES", "")
            if raw:
                params = dict(
                    part.split("=", 1)
                    for part in raw.split("&")
                    if "=" in part
                )
                # Named capture (:path*) → "path=...", positional (.*) → "1=..."
                path = urllib.parse.unquote(
                    params.get("path") or params.get("1") or ""
                )
                environ = environ.copy()
                environ["PATH_INFO"] = "/" + path if path else "/"
        return wsgi_app(environ, start_response)
    return application


app.wsgi_app = _vercel_path_fix(app.wsgi_app)
