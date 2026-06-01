def test_register(client):
    res = client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "dupuser", "password": "pass123"})
    res = client.post("/auth/register", json={"username": "dupuser", "password": "pass123"})
    assert res.status_code == 400


def test_login(client):
    client.post("/auth/register", json={"username": "loginuser", "password": "pass123"})
    res = client.post("/auth/login", json={"username": "loginuser", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "wrongpw", "password": "pass123"})
    res = client.post("/auth/login", json={"username": "wrongpw", "password": "wrong"})
    assert res.status_code == 401
