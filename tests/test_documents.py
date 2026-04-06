def test_upload_docx_creates_initial_operation(client, auth_headers, sample_docx_bytes):
    products_response = client.get("/api/v1/products", headers=auth_headers)
    product_id = products_response.json()["data"][0]["id"]

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"product_id": product_id, "policy_number": "POL-001"},
        files={
            "file": (
                "prepoliza.docx",
                sample_docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "RECEIVED"
    assert payload["data"]["policy_number"] == "POL-001"
    assert payload["data"]["original_filename"] == "prepoliza.docx"
    assert payload["data"]["original_path"].startswith("documents/originals/")
    assert payload["data"]["output_path"].startswith("documents/outputs/")



def test_upload_rejects_non_docx(client, auth_headers):
    products_response = client.get("/api/v1/products", headers=auth_headers)
    product_id = products_response.json()["data"][0]["id"]

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"product_id": product_id, "policy_number": "POL-002"},
        files={"file": ("archivo.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_file_extension"
