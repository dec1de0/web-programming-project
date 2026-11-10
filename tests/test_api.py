from fastapi.testclient import TestClient

from app.main import create_app


def test_project_crud_and_validation():
    client = TestClient(create_app())
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200

    assert client.post("/api/v1/projects", json={"name": "   "}).status_code == 422
    assert client.post("/api/v1/projects", json={"name": "Demo", "extra": 1}).status_code == 422
    created = client.post("/api/v1/projects", json={"name": "Demo", "description": "First"})
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.post("/api/v1/projects", json={"name": "demo"}).status_code == 409
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 200
    listing = client.get("/api/v1/projects?search=dem&offset=0&limit=1").json()
    assert listing["total"] == 1 and len(listing["items"]) == 1
    assert client.get("/api/v1/projects?limit=0").status_code == 422
    assert client.patch(f"/api/v1/projects/{project_id}", json={}).status_code == 422
    assert client.patch(f"/api/v1/projects/{project_id}", json={"name": None}).status_code == 422
    assert client.patch(f"/api/v1/projects/{project_id}", json={"name": "Renamed"}).json()["name"] == "Renamed"
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 404


def test_code_audit_findings_report_and_cascade():
    client = TestClient(create_app())
    project_id = client.post("/api/v1/projects", json={"name": "Code demo"}).json()["id"]
    base = f"/api/v1/projects/{project_id}/audits"
    assert client.post(base, json={"kind": "code", "source": ""}).status_code == 422
    assert client.post(base, json={"kind": "wrong", "source": "x"}).status_code == 422
    assert client.post("/api/v1/projects/00000000-0000-0000-0000-000000000000/audits",
                       json={"kind": "code", "source": "x = 1"}).status_code == 404
    result = client.post(base, json={"kind": "code", "source": "password = 'test'\neval('2+2')"})
    assert result.status_code == 201
    audit_id = result.json()["id"]
    assert result.json()["initial_score"] == 60
    assert client.get(base).json()["total"] == 1
    assert client.get(base + "?kind=design").json()["total"] == 0
    assert client.get(base + "?kind=other").status_code == 422
    assert client.get(f"/api/v1/audits/{audit_id}").status_code == 200
    findings_url = f"/api/v1/audits/{audit_id}/findings"
    found = client.get(findings_url)
    assert found.status_code == 200 and found.json()["total"] == 2
    assert client.get(findings_url + "?severity=high").json()["total"] == 2
    assert client.get(findings_url + "?status=resolved").json()["total"] == 0
    finding_id = found.json()["items"][0]["id"]
    finding_url = findings_url + "/" + finding_id
    assert client.patch(finding_url, json={"status": "resolved"}).status_code == 422
    assert client.patch(finding_url, json={"status": "resolved", "resolution_note": "Fixed"}).status_code == 200
    assert client.patch(finding_url, json={"status": "resolved", "resolution_note": "Again"}).status_code == 409
    report = client.get(f"/api/v1/audits/{audit_id}/report").json()
    assert (report["initial_score"], report["current_score"], report["resolved_count"]) == (60, 80, 1)
    assert client.patch(finding_url, json={"status": "open"}).status_code == 200
    assert client.get(f"/api/v1/audits/{audit_id}/report").json()["current_score"] == 60
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 204
    assert client.get(f"/api/v1/audits/{audit_id}").status_code == 404
    assert client.get(findings_url).status_code == 404
    assert client.get(f"/api/v1/audits/{audit_id}/report").status_code == 404


def test_design_audit_and_wrong_audit_finding():
    client = TestClient(create_app())
    project_id = client.post("/api/v1/projects", json={"name": "Design demo"}).json()["id"]
    base = f"/api/v1/projects/{project_id}/audits"
    assert client.post(base, json={"kind": "design", "elements": []}).status_code == 422
    design = {
        "kind": "design",
        "elements": [{"kind": "button", "label": "", "text_color": "#777777",
                      "background_color": "#777777", "font_size": 12, "width": 30, "height": 30}],
    }
    audit = client.post(base, json=design)
    assert audit.status_code == 201 and audit.json()["initial_score"] == 55
    audit_id = audit.json()["id"]
    finding_id = client.get(f"/api/v1/audits/{audit_id}/findings").json()["items"][0]["id"]
    second_id = client.post(base, json={"kind": "code", "source": "x = 1"}).json()["id"]
    assert client.patch(f"/api/v1/audits/{second_id}/findings/{finding_id}",
                        json={"status": "resolved", "resolution_note": "Done"}).status_code == 404
    assert client.get(f"/api/v1/audits/{second_id}/report").json()["current_score"] == 100
    assert client.get("/api/v1/audits/not-a-uuid").status_code == 422
