import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from coursekit.variant import load_variant


ROOT = Path(__file__).resolve().parents[3]
APP_PATH = ROOT / "weeks" / "week-02" / "app" / "main.py"


def load_app():
    spec = importlib.util.spec_from_file_location("week02_app_extra", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def sample_value(field_type):
    values = {
        "str": "demo",
        "int": 10,
        "float": 1.5,
        "bool": False,
    }
    return values[field_type]


def test_update_notification():
    variant = load_variant("02")
    resource = variant["resource"]
    extra = variant["extra_field"]
    client = TestClient(load_app())

    payload = {"name": "First", extra["name"]: sample_value(extra["type"])}
    created = client.post(f"/{resource}", json=payload).json()

    updated_payload = {"name": "Updated", extra["name"]: sample_value(extra["type"])}
    response = client.put(f"/{resource}/{created['id']}", json=updated_payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


def test_delete_unknown_notification():
    variant = load_variant("02")
    resource = variant["resource"]
    client = TestClient(load_app())

    response = client.delete(f"/{resource}/999")

    assert response.status_code == 404
