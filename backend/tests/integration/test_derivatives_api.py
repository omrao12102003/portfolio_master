import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_forward_api():
    response = client.post(
        "/quant/derivatives/forward",
        json={
            "spot": 100,
            "rate": 0.05,
            "time_to_maturity": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["forward_price"] == pytest.approx(105.1271, rel=1e-4)


def test_futures_api():
    response = client.post(
        "/quant/derivatives/futures",
        json={
            "spot": 100,
            "rate": 0.05,
            "time_to_maturity": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["futures_price"] == pytest.approx(105.1271, rel=1e-4)


def test_put_call_parity_api():
    response = client.post(
        "/quant/derivatives/put-call-parity",
        json={
            "call_price": 10.4506,
            "spot": 100,
            "strike": 100,
            "rate": 0.05,
            "time_to_maturity": 1,
        },
    )

    assert response.status_code == 200
    assert "put_price" in response.json()


def test_black_scholes_api():
    response = client.post(
        "/quant/derivatives/black-scholes",
        json={
            "spot": 100,
            "strike": 100,
            "rate": 0.05,
            "volatility": 0.20,
            "time_to_maturity": 1,
            "option_type": "call",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["price"] == pytest.approx(10.4506, rel=1e-4)
    assert set(payload["greeks"]) == {
        "delta",
        "gamma",
        "theta",
        "vega",
        "rho",
    }


def test_binomial_api():
    response = client.post(
        "/quant/derivatives/binomial",
        json={
            "spot": 100,
            "strike": 100,
            "rate": 0.05,
            "volatility": 0.20,
            "time_to_maturity": 1,
            "steps": 100,
        },
    )

    assert response.status_code == 200
    assert response.json()["steps"] == 100


def test_implied_volatility_api():
    response = client.post(
        "/quant/derivatives/implied-volatility",
        json={
            "market_price": 10.4506,
            "spot": 100,
            "strike": 100,
            "rate": 0.05,
            "time_to_maturity": 1,
            "option_type": "call",
        },
    )

    assert response.status_code == 200
    assert response.json()["implied_volatility"] == pytest.approx(
        0.20,
        abs=1e-4,
    )
