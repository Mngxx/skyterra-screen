"""Load synthetic data.

Roughly 50,000 tasks spread over a handful of areas, with tags in the JSONB
column. Deterministic: the same seed every run, so a timing you take today is
comparable to one you take tomorrow.

    python seed.py
"""

import random

from models import Area, SessionLocal, Task, reset_db


AREAS = [
    ("Platform", False),
    ("Billing", False),
    ("Reporting", False),
    ("Mobile", False),
    ("Legacy import", True),   # archived
]

TAGS = [
    "backend", "frontend", "urgent", "flaky", "customer-reported",
    "perf", "cleanup", "migration", "security", "docs",
]

TOTAL_TASKS = 250_000


def main():
    random.seed(20260803)
    reset_db()

    with SessionLocal() as session:
        areas = [Area(name=name, archived=archived) for name, archived in AREAS]
        session.add_all(areas)
        session.commit()

        live_area_ids = [a.id for a in areas if not a.archived]

        batch = []
        for n in range(TOTAL_TASKS):
            tags = random.sample(TAGS, random.randint(1, 3))
            # A small share of rows carry the same tag twice. This is real:
            # tags arrive from more than one source and nothing de-duplicates
            # them on the way in.
            if random.random() < 0.04:
                tags.append(tags[0])

            batch.append(Task(
                title=f"Task {n + 1}",
                area_id=random.choice(live_area_ids),
                status=random.choice(["open", "in_progress", "done"]),
                meta={
                    "tags": tags,
                    "estimate": random.choice([1, 2, 3, 5, 8]),
                    "reporter": f"user{random.randint(1, 400)}",
                },
            ))

            if len(batch) >= 5_000:
                session.add_all(batch)
                session.commit()
                batch = []
                print(f"  {n + 1} rows")

        if batch:
            session.add_all(batch)
            session.commit()

    print(f"Seeded {TOTAL_TASKS} tasks across {len(AREAS)} areas.")


if __name__ == "__main__":
    main()
