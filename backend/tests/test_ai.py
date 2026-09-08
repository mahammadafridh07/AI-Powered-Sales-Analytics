def test_ai_status_no_key_configured(client, auth_headers):
    res = client.get("/ai/status", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["ai_configured"] is False  # test env has no LLM_API_KEY set


def test_ai_chat_answers_without_crashing(client, auth_headers):
    res = client.post("/ai/chat", json={"question": "Which region generated the highest revenue?"}, headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["answer"]
    assert body["ai_configured"] is False


def test_ai_chat_handles_unknown_question_gracefully(client, auth_headers):
    res = client.post("/ai/chat", json={"question": "asdkjaslkdj random gibberish question"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["answer"]


def test_ai_insights_endpoint(client, auth_headers):
    res = client.get("/ai/insights", headers=auth_headers)
    assert res.status_code == 200
    assert "insights" in res.json()


def test_recommendations_endpoint(client, auth_headers):
    res = client.get("/recommendations", headers=auth_headers)
    assert res.status_code == 200
    assert "recommendations" in res.json()


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
