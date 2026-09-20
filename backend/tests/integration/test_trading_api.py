import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_momentum_api():
    response = client.post(
        "/quant/trading/signals/momentum",
        json={
            "prices": [100, 101, 102, 103, 104],
            "lookback": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["signal"] == [0.0, 0.0, 1.0, 1.0, 1.0]


def test_mean_reversion_api():
    response = client.post(
        "/quant/trading/signals/mean-reversion",
        json={
            "prices": [100, 100, 100, 100, 100, 110],
            "lookback": 5,
            "entry_zscore": 1.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["signal"][-1] == 0.0


def test_position_sizing_api():
    response = client.post(
        "/quant/trading/position-sizing",
        json={
            "signal": [1.0, -1.0, 1.0],
            "volatility": [0.05, 0.10, 0.50],
            "target_volatility": 0.10,
            "max_position": 1.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["positions"] == pytest.approx(
        [1.0, -1.0, 0.2]
    )


def test_evaluation_api():
    response = client.post(
        "/quant/trading/evaluate",
        json={
            "target_positions": [0.0, 1.0, 1.0, 0.0],
            "asset_returns": [0.0, 0.01, 0.02, -0.01],
            "transaction_cost_bps": 5,
            "slippage_bps": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["observations"] == 4
    assert payload["total_turnover"] == pytest.approx(2.0)
    assert "sharpe_ratio" in payload
    assert "maximum_drawdown" in payload


def test_walk_forward_api():
    response = client.post(
        "/quant/trading/walk-forward",
        json={
            "observations": 100,
            "train_size": 60,
            "test_size": 10,
            "step_size": 10,
        },
    )

    assert response.status_code == 200
    splits = response.json()["splits"]
    assert len(splits) == 4
    assert splits[0]["train_end"] == splits[0]["test_start"]
    assert splits[-1]["test_end"] == 100
