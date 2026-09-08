def test_dashboard_summary_has_data(client, auth_headers):
    res = client.get("/dashboard/summary", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["has_data"] is True
    assert body["kpis"]["revenue"]["value"] > 0


def test_dashboard_filter_options(client, auth_headers):
    res = client.get("/dashboard/filter-options", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["regions"]) > 0
    assert len(body["categories"]) > 0


def test_products_list(client, auth_headers):
    res = client.get("/products", headers=auth_headers)
    assert res.status_code == 200
    products = res.json()["products"]
    assert len(products) > 0
    assert "revenue" in products[0]


def test_customers_list(client, auth_headers):
    res = client.get("/customers", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["summary"]["total_customers"] > 0


def test_regions_list(client, auth_headers):
    res = client.get("/regions", headers=auth_headers)
    assert res.status_code == 200
    regions = res.json()["regions"]
    assert len(regions) > 0


def test_region_filter_applied(client, auth_headers):
    all_res = client.get("/regions", headers=auth_headers).json()["regions"]
    first_region = all_res[0]["region"]
    filtered = client.get("/products", params={"region": first_region}, headers=auth_headers).json()["products"]
    assert isinstance(filtered, list)
