def test_list_active_products(client, auth_headers):
    response = client.get("/api/v1/products", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]) == 1
    assert payload["data"][0]["code"] == "VIDA_TEST"
    assert payload["data"][0]["active_format_rule"]["version"] == 1
