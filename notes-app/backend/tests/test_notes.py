from tests.conftest import AUTH


def _make_note(client, title="First note", body="hello world", tags=None):
    payload = {"title": title, "body": body, "tags": tags or []}
    return client.post("/notes", json=payload, headers=AUTH)


# auth

def test_requires_api_key(client):
    resp = client.get("/notes")
    assert resp.status_code == 401
    assert "API key" in resp.json()["detail"]


def test_rejects_wrong_api_key(client):
    resp = client.get("/notes", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 403


# create note test

def test_create_note(client):
    resp = _make_note(client, tags=["Work", "work", " urgent "])
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "First note"
    assert data["tags"] == ["work", "urgent"]
    assert data["id"] > 0
    assert data["created_at"] and data["updated_at"]


def test_blank_title_is_rejected(client):
    resp = client.post("/notes", json={"title": "   ", "body": "x"}, headers=AUTH)
    assert resp.status_code == 422
    assert "title" in resp.json()["detail"].lower()


# read test

def test_get_and_list_notes(client):
    created = _make_note(client).json()
    got = client.get(f"/notes/{created['id']}", headers=AUTH)
    assert got.status_code == 200
    assert got.json()["id"] == created["id"]

    listed = client.get("/notes", headers=AUTH)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_get_missing_note_returns_404(client):
    resp = client.get("/notes/999", headers=AUTH)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# update note test

def test_update_note_partial(client):
    note = _make_note(client, title="Old", body="body").json()
    resp = client.put(
        f"/notes/{note['id']}", json={"title": "New title"}, headers=AUTH
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["title"] == "New title"
    assert updated["body"] == "body"


# delete note test

def test_delete_note(client):
    note = _make_note(client).json()
    resp = client.delete(f"/notes/{note['id']}", headers=AUTH)
    assert resp.status_code == 204
    assert client.get(f"/notes/{note['id']}", headers=AUTH).status_code == 404


# search for note test

def test_search_by_keyword_and_tag(client):
    _make_note(client, title="Grocery list", body="milk and eggs", tags=["home"])
    _make_note(client, title="Sprint plan", body="ship the API", tags=["work"])

    by_keyword = client.get("/notes/search", params={"q": "api"}, headers=AUTH)
    assert by_keyword.status_code == 200
    assert [n["title"] for n in by_keyword.json()] == ["Sprint plan"]

    by_tag = client.get("/notes/search", params={"tag": "home"}, headers=AUTH)
    assert [n["title"] for n in by_tag.json()] == ["Grocery list"]


def test_search_requires_a_parameter(client):
    resp = client.get("/notes/search", headers=AUTH)
    assert resp.status_code == 400
