def test_create_conversation(auth_client):
    res = auth_client.post("/conversations", json={"title": "Test Chat"})
    assert res.status_code == 200
    assert res.json()["title"] == "Test Chat"


def test_list_conversations(auth_client):
    auth_client.post("/conversations", json={"title": "Chat 1"})
    auth_client.post("/conversations", json={"title": "Chat 2"})
    res = auth_client.get("/conversations")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_rename_conversation(auth_client):
    res = auth_client.post("/conversations", json={"title": "Old Name"})
    conv_id = res.json()["id"]
    res = auth_client.put(f"/conversations/{conv_id}", json={"title": "New Name"})
    assert res.status_code == 200
    assert res.json()["title"] == "New Name"


def test_delete_conversation(auth_client):
    res = auth_client.post("/conversations", json={"title": "To Delete"})
    conv_id = res.json()["id"]
    res = auth_client.delete(f"/conversations/{conv_id}")
    assert res.status_code == 200
    res = auth_client.get("/conversations")
    assert len(res.json()) == 0
