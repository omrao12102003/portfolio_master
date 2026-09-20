import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_capm_api():
    market = [0.01, 0.02, -0.01, 0.03, 0.015]
    asset = [0.002 + 1.5 * value for value in market]

    response = client.post(
        "/quant/capm",
        json={
            "asset_returns": asset,
            "market_returns": market,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["alpha"] == pytest.approx(0.002)
    assert body["beta"] == pytest.approx(1.5)
    assert body["observations"] == 5


def test_fama_french_api():
    market = [0.01, 0.02, -0.01, 0.03, 0.015, -0.02]
    smb = [0.02, -0.01, 0.015, 0.01, -0.02, 0.005]
    hml = [-0.01, 0.015, 0.02, -0.005, 0.01, -0.015]

    asset = [
        0.002 + 1.2 * m + 0.7 * s - 0.4 * h
        for m, s, h in zip(market, smb, hml)
    ]

    response = client.post(
        "/quant/fama-french",
        json={
            "asset_returns": asset,
            "market_excess_returns": market,
            "smb_returns": smb,
            "hml_returns": hml,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["alpha"] == pytest.approx(0.002)
    assert body["market_beta"] == pytest.approx(1.2)
    assert body["smb_beta"] == pytest.approx(0.7)
    assert body["hml_beta"] == pytest.approx(-0.4)


def test_arima_api():
    rng = np.random.default_rng(42)
    values = np.cumsum(rng.normal(0.001, 0.01, 80)).tolist()

    response = client.post(
        "/quant/arima",
        json={
            "values": values,
            "p": 1,
            "d": 1,
            "q": 0,
            "steps": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["order"] == [1, 1, 0]
    assert len(body["forecast"]) == 5
    assert len(body["lower"]) == 5
    assert len(body["upper"]) == 5


def test_garch_api():
    rng = np.random.default_rng(42)
    returns = rng.normal(0, 0.01, 120).tolist()

    response = client.post(
        "/quant/garch",
        json={
            "returns": returns,
            "steps": 5,
            "annualization_factor": 252,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["forecast_variance"]) == 5
    assert len(body["forecast_volatility"]) == 5
    assert len(body["annualized_forecast_volatility"]) == 5


def test_factor_api_rejects_invalid_capm():
    response = client.post(
        "/quant/capm",
        json={
            "asset_returns": [0.01, 0.02],
            "market_returns": [0.01],
        },
    )

    assert response.status_code == 422
