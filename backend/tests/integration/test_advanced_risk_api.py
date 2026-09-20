import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_monte_carlo_var_api():
    rng = np.random.default_rng(42)
    returns = rng.normal(0.0005, 0.01, 300).tolist()

    response = client.post(
        "/quant/risk/monte-carlo-var",
        json={
            "returns": returns,
            "confidence": 0.95,
            "simulations": 2000,
            "seed": 42,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["var"] > 0
    assert body["expected_shortfall"] >= body["var"]
    assert body["simulations"] == 2000


def test_stress_test_api():
    response = client.post(
        "/quant/risk/stress-test",
        json={
            "weights": [0.5, 0.3, 0.2],
            "scenario_returns": [-0.1, -0.2, 0.05],
            "scenario_name": "market_crash",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["portfolio_return"] == pytest.approx(-0.10)
    assert body["scenario_name"] == "market_crash"


def test_factor_risk_api():
    response = client.post(
        "/quant/risk/factor",
        json={
            "factor_exposures": [1.2, 0.5],
            "factor_covariance": [
                [0.04, 0.01],
                [0.01, 0.025],
            ],
            "residual_variance": 0.01,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["systematic_variance"] > 0
    assert body["total_variance"] > body["systematic_variance"]
    assert (
        body["systematic_percentage"]
        + body["idiosyncratic_percentage"]
        == pytest.approx(1.0)
    )


def test_risk_attribution_api():
    response = client.post(
        "/quant/risk/attribution",
        json={
            "weights": [0.5, 0.3, 0.2],
            "covariance": [
                [0.04, 0.01, 0.005],
                [0.01, 0.025, 0.003],
                [0.005, 0.003, 0.016],
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_risk"] > 0
    assert sum(body["percentage_contributions"]) == pytest.approx(1.0)


def test_advanced_risk_api_rejects_invalid_stress_test():
    response = client.post(
        "/quant/risk/stress-test",
        json={
            "weights": [0.5, 0.5],
            "scenario_returns": [-0.1],
        },
    )

    assert response.status_code == 400
