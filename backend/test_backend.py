import pytest
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_lms.db"
if os.path.exists("test_lms.db"):
    try:
        os.remove("test_lms.db")
    except OSError:
        pass

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module", autouse=True)
def client():
    with TestClient(app) as c:
        yield c

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_login_and_me(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee@lms.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["employee_code"] == "EMP1001"

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "employee@lms.com"

def test_get_leave_balance(client):
    login_resp = client.post("/api/v1/auth/login", json={"email": "employee@lms.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    bal_resp = client.get("/api/v1/leaves/balance", headers=headers)
    assert bal_resp.status_code == 200
    bal_data = bal_resp.json()
    assert "annual" in bal_data
    assert "sick" in bal_data
    assert "casual" in bal_data

def test_apply_and_approve_leave(client):
    # Login Employee
    emp_resp = client.post("/api/v1/auth/login", json={"email": "jane@lms.com", "password": "password123"})
    emp_token = emp_resp.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Apply Leave
    apply_payload = {
        "leaveTypeId": 1,
        "startDate": "2026-10-10",
        "endDate": "2026-10-12",
        "reason": "Conference Attendance"
    }
    apply_resp = client.post("/api/v1/leaves", json=apply_payload, headers=emp_headers)
    assert apply_resp.status_code == 201
    res_data = apply_resp.json()
    assert "requestId" in res_data
    assert res_data["status"] == "PENDING"
    req_id = res_data["requestId"]

    # Login Manager
    mgr_resp = client.post("/api/v1/auth/login", json={"email": "manager@lms.com", "password": "password123"})
    mgr_token = mgr_resp.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    # Approve Leave
    approve_resp = client.post(f"/api/v1/leaves/{req_id}/approve", json={"comments": "Approved. Have fun!"}, headers=mgr_headers)
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "APPROVED"

def test_audit_logs(client):
    login_resp = client.post("/api/v1/auth/login", json={"email": "hr@lms.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    audit_resp = client.get("/api/v1/audit-logs", headers=headers)
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) > 0
    # Check sample format matching: event, performedBy, requestId, timestamp
    sample = logs[0]
    assert "event" in sample
    assert "performedBy" in sample
    assert "requestId" in sample
    assert "timestamp" in sample

if __name__ == "__main__":
    pytest.main(["-v", "backend/test_backend.py"])
