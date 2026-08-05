from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
app = Flask(__name__)
def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


conn = get_db_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT,
    created_at TEXT
)
""")

conn.commit()
conn.close()

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.execute(
        """
        INSERT INTO tasks (title, description, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            data["title"],
            data.get("description", ""),
            data.get("status", "pending"),
            created_at
        )
    )

    conn.commit()

    task = {
        "id": cursor.lastrowid,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": data.get("status", "pending"),
        "created_at": created_at
    }

    conn.close()

    return jsonify(task), 201

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()

    tasks = conn.execute("SELECT * FROM tasks").fetchall()

    conn.close()

    return jsonify([dict(task) for task in tasks])

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(dict(task))

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    if "title" in data and not data["title"]:
        return jsonify({"error": "Title cannot be empty"}), 400

    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    status = data.get("status", task["status"])

    conn.execute(
        """
        UPDATE tasks
        SET title=?, description=?, status=?
        WHERE id=?
        """,
        (title, description, status, task_id)
    )

    conn.commit()

    updated_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(updated_task))

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted successfully"})
if __name__ == "__main__":
    app.run(debug=True)