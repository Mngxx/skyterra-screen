"""The suite as it stands.

Everything here passes on a clean checkout. That is worth remembering while you
are working on task B.
"""


def test_areas_are_listed(client):
    response = client.get("/api/areas")
    assert response.status_code == 200
    names = {a["name"] for a in response.get_json()["areas"]}
    assert {"Platform", "Billing", "Legacy import"} <= names


def test_area_is_required(client):
    assert client.get("/api/tasks").status_code == 400


def test_tasks_are_scoped_to_their_area(client, area_ids):
    body = client.get(f"/api/tasks?area={area_ids['platform']}").get_json()
    titles = {t["title"] for t in body["tasks"]}
    assert titles == {"First", "Second"}


def test_duplicate_tags_are_not_double_counted(client, area_ids):
    client.post(
        "/api/tasks",
        json={
            "title": "Tagged twice",
            "area_id": area_ids["platform"],
            "meta": {"tags": ["backend", "backend"]},
        },
    )

    body = client.get(f"/api/tasks?area={area_ids['platform']}&tag=backend").get_json()

    assert body["count"] == len(body["tasks"])
    assert body["count"] == 2


def test_tag_filter_selects_the_right_tasks(client, area_ids):
    body = client.get(f"/api/tasks?area={area_ids['platform']}&tag=backend").get_json()
    assert [t["title"] for t in body["tasks"]] == ["First"]


def test_tag_filter_that_matches_nothing(client, area_ids):
    body = client.get(f"/api/tasks?area={area_ids['platform']}&tag=nonsense").get_json()
    assert body["tasks"] == []


def test_a_task_is_created_in_the_area_it_names(client, area_ids):
    response = client.post(
        "/api/tasks",
        json={
            "title": "Created by the suite",
            "area_id": area_ids["billing"],
        },
    )
    assert response.status_code == 201
    assert response.get_json()["area_id"] == area_ids["billing"]


def test_title_is_required(client, area_ids):
    response = client.post(
        "/api/tasks",
        json={
            "title": "   ",
            "area_id": area_ids["platform"],
        },
    )
    assert response.status_code == 400


def test_an_area_that_does_not_exist_is_rejected(client):
    response = client.post(
        "/api/tasks",
        json={
            "title": "Nowhere",
            "area_id": 999_999,
        },
    )
    assert response.status_code == 400


def test_meta_round_trips(client, area_ids):
    response = client.post(
        "/api/tasks",
        json={
            "title": "With meta",
            "area_id": area_ids["platform"],
            "meta": {"tags": ["perf"], "estimate": 3},
        },
    )
    assert response.status_code == 201
    assert response.get_json()["meta"]["estimate"] == 3
