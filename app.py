"""
Flask app for Vercel + local dev. Single file so the serverless bundle always includes all routes.
"""

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
            # Avoid 204 + empty body; some serverless/WSGI stacks mishandle it.
            return jsonify({"ok": True}), 200
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
