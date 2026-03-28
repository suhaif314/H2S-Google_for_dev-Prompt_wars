"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_has_status(self):
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TriageAI"
        assert "version" in data
        assert "timestamp" in data

    def test_health_shows_gcp_project(self):
        response = client.get("/api/health")
        data = response.json()
        assert "gcp_project" in data


class TestTriageEndpoint:
    def test_no_input_returns_400(self):
        response = client.post("/api/triage")
        assert response.status_code == 400

    def test_empty_text_returns_400(self):
        response = client.post("/api/triage", data={"text": ""})
        assert response.status_code == 400

    def test_invalid_audio_type(self):
        # Send a non-audio file as voice_file
        response = client.post(
            "/api/triage",
            files={"voice_file": ("test.txt", b"not audio", "text/plain")},
        )
        assert response.status_code == 400

    def test_invalid_doc_type(self):
        # Send a non-PDF as document
        response = client.post(
            "/api/triage",
            files={"document_file": ("test.txt", b"not a pdf", "text/plain")},
        )
        assert response.status_code == 400


class TestReportsEndpoint:
    def test_list_reports_returns_200(self):
        response = client.get("/api/reports")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "reports" in data

    def test_get_nonexistent_report_returns_404(self):
        response = client.get("/api/reports/nonexistent-id")
        assert response.status_code == 404


class TestFrontendServing:
    def test_root_returns_html(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_static_css(self):
        response = client.get("/static/css/styles.css")
        assert response.status_code == 200

    def test_static_js(self):
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
