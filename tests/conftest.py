import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The suite runs against its OWN database and drops every table between tests,
# so it must never point at the one you seeded for the task A timings. Set
# TEST_DATABASE_URL if you are not using the bundled docker-compose.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://screen:screen@localhost:55432/screen_test",
)

from app import app as flask_app           # noqa: E402
from models import Area, SessionLocal, Task, reset_db   # noqa: E402


@pytest.fixture()
def client():
    """A fresh, tiny database for each test.

    Not the 50,000-row seed. These tests are about behaviour, not timing.
    """
    reset_db()
    with SessionLocal() as session:
        platform = Area(name="Platform", archived=False)
        billing = Area(name="Billing", archived=False)
        legacy = Area(name="Legacy import", archived=True)
        session.add_all([platform, billing, legacy])
        session.commit()

        session.add_all([
            Task(title="First", area_id=platform.id, status="open",
                 meta={"tags": ["backend", "urgent"]}),
            Task(title="Second", area_id=platform.id, status="open",
                 meta={"tags": ["frontend"]}),
            Task(title="Third", area_id=billing.id, status="done",
                 meta={"tags": ["backend"]}),
        ])
        session.commit()

        flask_app.config.update(TESTING=True)
        flask_app.config["AREA_IDS"] = {
            "platform": platform.id,
            "billing": billing.id,
            "legacy": legacy.id,
        }

    with flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def area_ids():
    return flask_app.config["AREA_IDS"]
