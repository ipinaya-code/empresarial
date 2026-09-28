"""Navegador real sobre API; el recorrido de UI de pasajeros pertenece al backlog."""

import os

import pytest

pytestmark = pytest.mark.browser


def test_browser_can_reach_api(page):
    base_url = os.getenv("BROWSER_API_URL", "http://127.0.0.1:8000")
    response = page.goto(f"{base_url}/api/v1/health")
    assert response.status == 200
    assert '"status":"ok"' in page.locator("body").inner_text()
    assert page.request.get(f"{base_url}/api/v1/health/ready").ok
    schema = page.request.get(f"{base_url}/openapi.json").json()
    assert "/api/v1/reservar/seguro" in schema["paths"]
