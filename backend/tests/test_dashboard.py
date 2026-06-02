import pytest
from datetime import datetime

from app.models.conversation import Message


@pytest.fixture
def sample_data(auth_client):
    """创建一些测试数据"""
    res = auth_client.post("/conversations", json={"title": "测试对话"})
    conv_id = res.json()["id"]

    # 通过 API 创建消息会触发 AI 调用，直接用 HTTP 不行
    # 改为在测试中直接验证 API 返回结构即可
    return conv_id


def test_stats_empty(auth_client):
    res = auth_client.get("/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["conversation_count"] == 0
    assert data["message_count"] == 0
    assert data["card_count"] == 0
    assert data["active_days"] == 0
    assert len(data["daily_messages"]) == 30
    assert data["top_tags"] == []


def test_stats_structure(auth_client):
    """验证返回结构正确"""
    res = auth_client.get("/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "conversation_count" in data
    assert "message_count" in data
    assert "card_count" in data
    assert "active_days" in data
    assert "daily_messages" in data
    assert "top_tags" in data
    assert isinstance(data["daily_messages"], list)
    assert isinstance(data["top_tags"], list)
    # 每天数据有 date 和 count
    if data["daily_messages"]:
        assert "date" in data["daily_messages"][0]
        assert "count" in data["daily_messages"][0]


def test_stats_unauthorized(client):
    res = client.get("/dashboard/stats")
    assert res.status_code == 403
