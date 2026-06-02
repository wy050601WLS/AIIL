from unittest.mock import patch


def _create_conv(auth_client, title="Test"):
    res = auth_client.post("/conversations", json={"title": title})
    return res.json()["id"]


def _add_message(auth_client, conv_id, role, content):
    """直接往数据库插消息（跳过 AI 调用）"""
    from tests.conftest import TestingSessionLocal
    from app.models.conversation import Message

    db = TestingSessionLocal()
    msg = Message(conversation_id=conv_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    db.close()
    return msg.id


def test_edit_message(auth_client):
    conv_id = _create_conv(auth_client)
    msg_id = _add_message(auth_client, conv_id, "user", "原始内容")

    res = auth_client.put(f"/messages/{msg_id}", json={"content": "修改后的内容"})
    assert res.status_code == 200
    assert res.json()["content"] == "修改后的内容"


def test_edit_message_empty_content(auth_client):
    conv_id = _create_conv(auth_client)
    msg_id = _add_message(auth_client, conv_id, "user", "原始内容")

    res = auth_client.put(f"/messages/{msg_id}", json={"content": ""})
    assert res.status_code == 422


def test_delete_message(auth_client):
    conv_id = _create_conv(auth_client)
    msg_id = _add_message(auth_client, conv_id, "user", "要删除的消息")

    res = auth_client.delete(f"/messages/{msg_id}")
    assert res.status_code == 200


def test_delete_message_not_found(auth_client):
    res = auth_client.delete("/messages/99999")
    assert res.status_code == 404


def test_edit_message_other_user(auth_client, client):
    conv_id = _create_conv(auth_client)
    msg_id = _add_message(auth_client, conv_id, "user", "用户A的消息")

    # 注册另一个用户
    client.post("/auth/register", json={"username": "other", "password": "pass123456"})
    res = client.post("/auth/login", json={"username": "other", "password": "pass123456"})
    other_token = res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {other_token}"

    res = client.put(f"/messages/{msg_id}", json={"content": "越权修改"})
    assert res.status_code == 403
