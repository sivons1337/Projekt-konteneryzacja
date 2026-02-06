from flask import Flask, jsonify, request
import os
import mysql.connector

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "mariadb")
DB_NAME = os.environ.get("DB_NAME", "projekt_db")
DB_USER = os.environ.get("DB_USER", "projekt")
DB_PASS = os.environ.get("DB_PASS", "projekt123")

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )

def get_task_by_name(cur, name):
    cur.execute("SELECT id, name, status, created_at, updated_at FROM tasks WHERE name=%s", (name,))
    row = cur.fetchone()
    if not row:
        return None
    return {"id": row[0], "name": row[1], "status": row[2], "created_at": row[3].isoformat(), "updated_at": row[4].isoformat()}

@app.get("/api/tasks")
def list_tasks():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, status, created_at, updated_at FROM tasks ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    tasks = [
        {"id": r[0], "name": r[1], "status": r[2], "created_at": r[3].isoformat(), "updated_at": r[4].isoformat()}
        for r in rows
    ]
    return jsonify(tasks)

@app.post("/api/tasks")
def add_task():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Brak nazwy zadania"}), 400

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO tasks (name, status) VALUES (%s, 'PENDING')", (name,))
        conn.commit()
        task = get_task_by_name(cur, name)
        return jsonify({"ok": True, "task": task}), 201
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"ok": False, "error": f"Nie można dodać zadania: {str(e)}"}), 409
    finally:
        cur.close(); conn.close()

@app.post("/api/tasks/<int:task_id>/done")
def mark_done(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='DONE' WHERE id=%s", (task_id,))
    conn.commit()
    cur.execute("SELECT id, name, status, created_at, updated_at FROM tasks WHERE id=%s", (task_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return jsonify({"ok": False, "error": "Nie znaleziono zadania"}), 404
    task = {"id": row[0], "name": row[1], "status": row[2], "created_at": row[3].isoformat(), "updated_at": row[4].isoformat()}
    return jsonify({"ok": True, "task": task})

@app.get("/api/status")
def status():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT status, updated_at FROM tasks WHERE name=%s", ("projekt_zaliczeniowy",))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row:
        return jsonify({"task": "projekt_zaliczeniowy", "status": row[0], "updated_at": row[1].isoformat()})
    return jsonify({"task": "projekt_zaliczeniowy", "status": "PENDING", "updated_at": None})

@app.post("/api/task-done")
def task_done_legacy():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='DONE' WHERE name=%s", ("projekt_zaliczeniowy",))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok": True, "task": "projekt_zaliczeniowy", "status": "DONE"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)