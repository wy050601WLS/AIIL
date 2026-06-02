def _create_conv(auth_client, title="Test"):
    res = auth_client.post("/conversations", json={"title": title})
    return res.json()["id"]


def test_pin_conversation(auth_client):
    conv_id = _create_conv(auth_client)
    res = auth_client.put(f"/conversations/{conv_id}/pin")
    assert res.status_code == 200
    assert res.json()["pinned"] is True

    res = auth_client.put(f"/conversations/{conv_id}/pin")
    assert res.json()["pinned"] is False


def test_archive_conversation(auth_client):
    conv_id = _create_conv(auth_client)
    res = auth_client.put(f"/conversations/{conv_id}/archive")
    assert res.status_code == 200
    assert res.json()["archived"] is True

    res = auth_client.put(f"/conversations/{conv_id}/archive")
    assert res.json()["archived"] is False


def test_update_profile(auth_client):
    res = auth_client.put("/auth/profile", json={
        "nickname": "小明",
        "avatar": "🧑‍💻",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["nickname"] == "小明"
    assert data["avatar"] == "🧑‍💻"


def test_update_preferences(auth_client):
    import json
    prefs = json.dumps({"fontSize": 16, "messageDensity": "compact"})
    res = auth_client.put("/auth/profile", json={"preferences": prefs})
    assert res.status_code == 200
    assert res.json()["preferences"] == prefs


def test_change_password(auth_client, client):
    res = auth_client.put("/auth/password", json={
        "old_password": "testpass123",
        "new_password": "newpass123",
    })
    assert res.status_code == 200

    # 用新密码登录
    res = client.post("/auth/login", json={
        "username": "testuser",
        "password": "newpass123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_change_password_wrong_old(auth_client):
    res = auth_client.put("/auth/password", json={
        "old_password": "wrongpass",
        "new_password": "newpass123",
    })
    assert res.status_code == 400


def test_get_models(auth_client):
    res = auth_client.get("/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) > 0
