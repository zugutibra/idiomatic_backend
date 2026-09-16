def test_list_idioms(client):
    resp = client.get("/idioms")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_idioms_filtered_by_topic(client):
    resp = client.get("/idioms", params={"topic": "education"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["phrase"] == "Hit the books"


def test_due_idioms_includes_new_idioms(client, auth_headers):
    resp = client.get("/idioms/due", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(item["is_new"] for item in data)


def test_review_moves_idiom_up_a_box_and_out_of_due(client, auth_headers):
    idiom_id = client.get("/idioms").json()[0]["id"]

    review = client.post(f"/idioms/{idiom_id}/review", json={"correct": True}, headers=auth_headers)
    assert review.status_code == 200
    assert review.json()["box_level"] == 2

    due = client.get("/idioms/due", headers=auth_headers).json()
    assert idiom_id not in [d["id"] for d in due]


def test_review_incorrect_resets_to_box_one(client, auth_headers):
    idiom_id = client.get("/idioms").json()[0]["id"]
    client.post(f"/idioms/{idiom_id}/review", json={"correct": True}, headers=auth_headers)
    review = client.post(f"/idioms/{idiom_id}/review", json={"correct": False}, headers=auth_headers)
    assert review.json()["box_level"] == 1


def test_quiz_options_returns_one_correct_option(client):
    idiom_id = client.get("/idioms").json()[0]["id"]
    resp = client.get(f"/idioms/{idiom_id}/quiz-options")
    assert resp.status_code == 200
    options = resp.json()["options"]
    assert sum(1 for o in options if o["is_correct"]) == 1
