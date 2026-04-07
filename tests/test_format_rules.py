def test_create_update_list_and_delete_format_rule(client, auth_headers):
    products_response = client.get("/api/v1/products", headers=auth_headers)
    product_id = products_response.json()["data"][0]["id"]

    create_response = client.post(
        "/api/v1/format-rules",
        headers=auth_headers,
        json={
            "product_id": product_id,
            "active": True,
            "configuration": {
                "page_setup": {
                    "paper_size": "LETTER",
                    "margins": {"top_cm": 2.0, "bottom_cm": 2.0, "left_cm": 2.0, "right_cm": 2.0},
                },
                "general_text": {
                    "font_family": "Calibri",
                    "font_size_pt": 11,
                    "line_spacing": 1.2,
                    "uppercase": True,
                    "color_hex": "112233",
                },
                "title_text": {
                    "font_family": "Calibri",
                    "font_size_pt": 16,
                    "uppercase": True,
                    "alignment": "center",
                    "bold": True,
                },
            },
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()["data"]
    assert created["version"] == 2
    assert created["active"] is True
    assert created["configuration"]["general_text"]["uppercase"] is True

    list_response = client.get(f"/api/v1/format-rules?product_id={product_id}", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 2

    update_response = client.put(
        f"/api/v1/format-rules/{created['id']}",
        headers=auth_headers,
        json={
            "active": True,
            "configuration": {
                "page_setup": {
                    "paper_size": "A4",
                    "margins": {"top_cm": 3.0, "bottom_cm": 3.0, "left_cm": 2.5, "right_cm": 2.5},
                },
                "general_text": {
                    "font_family": "Arial",
                    "font_size_pt": 10,
                    "line_spacing": 1.0,
                    "uppercase": False,
                    "color_hex": "000000",
                },
                "title_text": {
                    "font_family": "Arial",
                    "font_size_pt": 15,
                    "uppercase": False,
                    "alignment": "left",
                    "bold": True,
                },
            },
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["version"] == 3
    assert updated["configuration"]["page_setup"]["margins"]["top_cm"] == 3.0

    delete_response = client.delete(f"/api/v1/format-rules/{updated['id']}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["active"] is False
