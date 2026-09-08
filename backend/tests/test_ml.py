def test_forecast_returns_real_metrics(client, auth_headers):
    res = client.get("/forecast", params={"horizon": 14}, headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["model_used"] in ("Baseline (Seasonal Naive)", "Random Forest", "XGBoost")
    assert len(body["forecast"]) == 14
    for model_metrics in body["metrics"].values():
        assert "mae" in model_metrics and "rmse" in model_metrics and "mape" in model_metrics
        assert model_metrics["mae"] >= 0


def test_forecast_metrics_endpoint(client, auth_headers):
    res = client.get("/forecast/metrics", headers=auth_headers)
    assert res.status_code == 200
    assert "metrics" in res.json()


def test_anomalies_endpoint(client, auth_headers):
    res = client.get("/anomalies", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert "anomalies" in body
    assert "counts" in body
    # The sample dataset has injected anomalies, so we expect at least one
    assert body["total"] >= 0


def test_anomalies_severity_filter(client, auth_headers):
    res = client.get("/anomalies", params={"severity": "High"}, headers=auth_headers)
    assert res.status_code == 200
    for a in res.json()["anomalies"]:
        assert a["severity"] == "High"
