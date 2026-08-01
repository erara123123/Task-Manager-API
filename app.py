from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

tasks = []
next_id = 1


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id

    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    task = {
        "id": next_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": data.get("status", "pending"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    tasks.append(task)
    next_id += 1

    return jsonify(task), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            return jsonify(task)

    return jsonify({"error": "Task not found"}), 404


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    for task in tasks:
        if task["id"] == task_id:

            if "title" in data and not data["title"]:
                return jsonify({"error": "Title cannot be empty"}), 400

            task["title"] = data.get("title", task["title"])
            task["description"] = data.get("description", task["description"])
            task["status"] = data.get("status", task["status"])

            return jsonify(task)

    return jsonify({"error": "Task not found"}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks

    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return jsonify({"message": "Task deleted successfully"})

    return jsonify({"error": "Task not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)