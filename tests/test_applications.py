NEW_APPLICATION = {
    "company": "Arelance",
    "position": "Python Developer",
    "status": "applied",
}


def test_applications_require_authentication(client):
    assert client.get("/applications").status_code == 401
    assert client.post("/applications", json=NEW_APPLICATION).status_code == 401


def test_create_and_list_application(client, make_user):
    headers = make_user("ana")

    created = client.post("/applications", json=NEW_APPLICATION, headers=headers)
    listed = client.get("/applications", headers=headers)

    assert created.status_code == 201
    assert created.json()["company"] == "Arelance"
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_default_status_is_saved(client, make_user):
    headers = make_user("ana")

    response = client.post(
        "/applications",
        json={"company": "Acme", "position": "Backend"},
        headers=headers,
    )

    assert response.json()["status"] == "saved"


def test_invalid_status_returns_422(client, make_user):
    headers = make_user("ana")

    response = client.post(
        "/applications",
        json={**NEW_APPLICATION, "status": "xyz"},
        headers=headers,
    )

    assert response.status_code == 422


def test_filter_by_status(client, make_user):
    headers = make_user("ana")
    client.post("/applications", json=NEW_APPLICATION, headers=headers)
    client.post(
        "/applications",
        json={"company": "Acme", "position": "Backend", "status": "saved"},
        headers=headers,
    )

    response = client.get("/applications?status=applied", headers=headers)

    assert [a["company"] for a in response.json()] == ["Arelance"]


def test_pagination(client, make_user):
    headers = make_user("ana")
    for i in range(3):
        client.post(
            "/applications",
            json={"company": f"Company {i}", "position": "Dev"},
            headers=headers,
        )

    response = client.get("/applications?limit=2&offset=2", headers=headers)

    assert len(response.json()) == 1


def test_partial_update_changes_only_sent_fields(client, make_user):
    headers = make_user("ana")
    created = client.post("/applications", json=NEW_APPLICATION, headers=headers).json()

    response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "interview"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interview"
    assert response.json()["company"] == "Arelance"


def test_delete_application(client, make_user):
    headers = make_user("ana")
    created = client.post("/applications", json=NEW_APPLICATION, headers=headers).json()

    deleted = client.delete(f"/applications/{created['id']}", headers=headers)
    fetched = client.get(f"/applications/{created['id']}", headers=headers)

    assert deleted.status_code == 204
    assert fetched.status_code == 404


def test_user_cannot_access_another_users_application(client, make_user):
    ana = make_user("ana")
    luis = make_user("luis")
    created = client.post("/applications", json=NEW_APPLICATION, headers=ana).json()
    url = f"/applications/{created['id']}"

    assert client.get("/applications", headers=luis).json() == []
    assert client.get(url, headers=luis).status_code == 404
    assert client.patch(url, json={"status": "offer"}, headers=luis).status_code == 404
    assert client.delete(url, headers=luis).status_code == 404

    still_there = client.get(url, headers=ana)
    assert still_there.status_code == 200
    assert still_there.json()["status"] == "applied"