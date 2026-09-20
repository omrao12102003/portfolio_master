import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_bond_price_api():
    response = client.post(
        "/quant/fixed-income/price",
        json={
            "face_value": 1000,
            "coupon_rate": 0.05,
            "yield_rate": 0.05,
            "maturity": 5,
            "frequency": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["price"] == pytest.approx(1000.0)


def test_ytm_api():
    response = client.post(
        "/quant/fixed-income/ytm",
        json={
            "price": 957.349,
            "face_value": 1000,
            "coupon_rate": 0.05,
            "maturity": 5,
            "frequency": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["yield_to_maturity"] == pytest.approx(
        0.06,
        abs=1e-4,
    )


def test_bond_analytics_api():
    response = client.post(
        "/quant/fixed-income/analytics",
        json={
            "face_value": 1000,
            "coupon_rate": 0.05,
            "yield_rate": 0.05,
            "maturity": 5,
            "frequency": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["price"] == pytest.approx(1000.0)
    assert payload["macaulay_duration"] > 0
    assert payload["modified_duration"] > 0
    assert payload["convexity"] > 0


def test_yield_curve_api():
    response = client.post(
        "/quant/fixed-income/yield-curve",
        json={
            "maturities": [1, 2, 5, 10],
            "spot_rates": [0.03, 0.035, 0.04, 0.045],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["maturities"]) == 4
    assert len(payload["discount_factors"]) == 4
    assert payload["discount_factors"][0] == pytest.approx(
        0.9704455,
        rel=1e-5,
    )


def test_rate_sensitivity_api():
    response = client.post(
        "/quant/fixed-income/rate-sensitivity",
        json={
            "price": 1000,
            "modified_duration": 4.3,
            "convexity": 25,
            "yield_change": 0.01,
        },
    )

    assert response.status_code == 200
    assert response.json()["estimated_price"] == pytest.approx(
        958.25,
        rel=1e-5,
    )
