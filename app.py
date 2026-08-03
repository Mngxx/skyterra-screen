"""A miniature task board.

Three routes. Two of them have something wrong with them; the README says which
exercise goes with which. Read it before changing anything.
"""

from flask import Flask, jsonify, render_template, request
from sqlalchemy import select

from models import Area, SessionLocal, Task, init_db


app = Flask(__name__)


def _last_used_area_id(session):
    """The area of the most recently created task.

    Used as the fallback when a request does not name an area. A real board
    remembers where you were working; this is the cheap version of that.
    """
    row = session.execute(
        select(Task.area_id).order_by(Task.id.desc()).limit(1)
    ).scalar_one_or_none()
    if row is not None:
        return row
    return session.execute(
        select(Area.id).order_by(Area.id).limit(1)
    ).scalar_one_or_none()


@app.get("/")
def index():
    with SessionLocal() as session:
        areas = session.execute(
            select(Area).where(Area.archived.is_(False)).order_by(Area.name)
        ).scalars().all()
    return render_template("index.html", areas=areas)


@app.get("/api/areas")
def list_areas():
    with SessionLocal() as session:
        areas = session.execute(select(Area).order_by(Area.name)).scalars().all()
        return jsonify({
            "areas": [
                {"id": a.id, "name": a.name, "archived": a.archived} for a in areas
            ]
        })


@app.get("/api/tasks")
def list_tasks():
    """Tasks in an area, optionally filtered to one tag.

    Returns the matching tasks and how many there are.
    """
    area_id = request.args.get("area", type=int)
    tag = request.args.get("tag")
    if area_id is None:
        return jsonify({"error": "area is required"}), 400

    with SessionLocal() as session:
        rows = session.execute(
            select(Task).where(Task.area_id == area_id).order_by(Task.id)
        ).scalars().all()

        if tag:
            matching = [t for t in rows if tag in (t.meta or {}).get("tags", [])]
            count = sum(
                len([x for x in (t.meta or {}).get("tags", []) if x == tag])
                for t in rows
            )
        else:
            matching = rows
            count = len(rows)

        return jsonify({
            "count": count,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "area_id": t.area_id,
                    "status": t.status,
                    "meta": t.meta,
                }
                for t in matching
            ],
        })


@app.post("/api/tasks")
def create_task():
    """Create a task in the named area."""
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    with SessionLocal() as session:
        area_id = payload.get("area_id") or _last_used_area_id(session)
        area = session.get(Area, area_id)
        if area is None or area.archived:
            return jsonify({"error": "unknown area"}), 400

        task = Task(
            title=title,
            area_id=area.id,
            status=payload.get("status") or "open",
            meta=payload.get("meta") or {},
        )
        session.add(task)
        session.commit()
        return jsonify({
            "id": task.id,
            "title": task.title,
            "area_id": task.area_id,
            "status": task.status,
            "meta": task.meta,
        }), 201


if __name__ == "__main__":
    init_db()
    app.run(port=5057, debug=True)
