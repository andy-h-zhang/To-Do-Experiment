"""Flask API as Vercel Python function (`/api/index`); static UI lives in `public/`."""

import urllib.parse
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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


def _vercel_path_fix(wsgi_app):
    """Restore original PATH_INFO when Vercel's rewrite overwrites it with the destination.

    Vercel sets PATH_INFO to the rewrite *destination* (/api/index) rather than
    the original request path (/api/todos).  It also sends the captured route
    parameters in the x-now-route-matches header, e.g. "path=todos%2F1", which
    lets us reconstruct the real path before Flask does its URL matching.
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
                path = urllib.parse.unquote(params.get("path", ""))
                if path:
                    environ = environ.copy()
                    environ["PATH_INFO"] = "/api/" + path
        return wsgi_app(environ, start_response)
    return application


app.wsgi_app = _vercel_path_fix(app.wsgi_app)
