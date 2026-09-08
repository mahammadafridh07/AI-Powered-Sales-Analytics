import io
from app.services import upload_service


def test_validate_missing_columns():
    import pandas as pd
    df = pd.DataFrame({"foo": [1, 2]})
    ok, errors = upload_service.validate(df)
    assert not ok
    assert any("Missing required columns" in e for e in errors)


def test_validate_empty_dataframe():
    import pandas as pd
    df = pd.DataFrame(columns=upload_service.REQUIRED_COLUMNS)
    ok, errors = upload_service.validate(df)
    assert not ok


def test_clean_drops_bad_rows():
    import pandas as pd
    df = pd.DataFrame({
        "order_date": ["2024-01-01", "not-a-date", "2024-01-03"],
        "customer_id": [1, 2, 3],
        "customer_name": ["A", "B", "C"],
        "region": ["North", "South", "East"],
        "product_id": [1, 2, 3],
        "product_name": ["P1", "P2", "P3"],
        "category": ["Cat1", "Cat1", "Cat2"],
        "quantity": [1, -5, 2],
        "unit_price": [100, 200, 300],
        "revenue": [100, 200, 600],
        "profit": [10, 20, 60],
    })
    cleaned = upload_service.clean(df)
    # Row index 1 has both an invalid date and negative quantity -- it should be dropped,
    # leaving the other two valid rows.
    assert len(cleaned) == 2
    assert set(cleaned["customer_name"]) == {"A", "C"}


def test_upload_endpoint_invalid_file(client, auth_headers):
    bad_csv = io.BytesIO(b"foo,bar\n1,2\n")
    res = client.post(
        "/upload",
        headers=auth_headers,
        files={"file": ("bad.csv", bad_csv, "text/csv")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "failed"
    assert body["error_message"] is not None


def test_upload_endpoint_valid_file(client, auth_headers):
    csv_content = (
        "order_date,customer_id,customer_name,region,product_id,product_name,category,quantity,unit_price,revenue,profit\n"
        "2024-01-01,9001,Test Customer,North,9001,Test Product,TestCat,2,500,1000,200\n"
    )
    res = client.post(
        "/upload",
        headers=auth_headers,
        files={"file": ("good.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "complete"
    assert body["rows_processed"] == 1
