"""Tests for the streams CRUD endpoints."""


def test_create_list_get_delete_stream(client):
    create_resp = client.post(
        "/api/v1/streams/",
        json={"name": "Test Stream", "source_url": "rtmp://localhost/live/test", "protocol": "RTMP"},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["name"] == "Test Stream"
    assert body["is_active"] is True
    stream_id = body["id"]

    list_resp = client.get("/api/v1/streams/")
    assert list_resp.status_code == 200
    assert any(s["id"] == stream_id for s in list_resp.json())

    get_resp = client.get(f"/api/v1/streams/{stream_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["source_url"] == "rtmp://localhost/live/test"

    delete_resp = client.delete(f"/api/v1/streams/{stream_id}")
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"/api/v1/streams/{stream_id}")
    assert missing_resp.status_code == 404


def test_get_nonexistent_stream_returns_404(client):
    response = client.get("/api/v1/streams/999999")
    assert response.status_code == 404
