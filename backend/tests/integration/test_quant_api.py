import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


PORTFOLIO_PAYLOAD = {
    "assets": ["A", "B", "C"],
    "expected_returns": [0.08, 0.12, 0.06],
    "covariance": [
        [0.04, 0.01, 0.00],
        [0.01, 0.09, 0.01],
        [0.00, 0.01, 0.01],
    ],
}


def test_returns_endpoint():
    response = client.post(
        "/quant/returns",
        json={"returns": [0.01, -0.005, 0.02, 0.01]},
    )

    assert response.status_code == 200
    body = response.json()

    assert "cumulative_return" in body
    assert "annualized_volatility" in body
    assert "sharpe_ratio" in body
    assert "sortino_ratio" in body
    assert "maximum_drawdown" in body


def test_risk_endpoint():
    response = client.post(
        "/quant/risk",
        json={"returns": [-0.02, 0.01, -0.01, 0.02, 0.0]},
    )

    assert response.status_code == 200
    body = response.json()

    assert "historical_var_95" in body
    assert "parametric_var_95" in body
    assert "expected_shortfall_95" in body


def test_optimize_endpoint():
    response = client.post(
        "/quant/optimize",
        json=PORTFOLIO_PAYLOAD,
    )

    assert response.status_code == 200
    body = response.json()

    assert set(body) == {
        "equal_weight",
        "minimum_volatility",
        "maximum_sharpe",
        "risk_parity",
    }

    for weights in body.values():
        assert sum(weights.values()) == pytest.approx(1.0)


def test_frontier_endpoint():
    response = client.post(
        "/quant/frontier",
        json=PORTFOLIO_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 20
    assert {
        "target_return",
        "expected_return",
        "volatility",
    }.issubset(body[0])


def test_backtest_endpoint():
    response = client.post(
        "/quant/backtest",
        json={
            "dates": [
                "2026-01-05",
                "2026-01-06",
                "2026-01-07",
                "2026-01-08",
                "2026-01-09",
            ],
            "assets": ["A", "B"],
            "prices": [
                [100, 100],
                [102, 101],
                [101, 103],
                [104, 102],
                [106, 105],
            ],
            "weights": [0.6, 0.4],
            "initial_capital": 100000,
            "transaction_cost_bps": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "summary" in body
    assert "equity_curve" in body
    assert "portfolio_returns" in body
    assert body["summary"]["final_capital"] > 0


def test_concentration_endpoint():
    response = client.post(
        "/quant/concentration",
        json=PORTFOLIO_PAYLOAD,
    )

    assert response.status_code == 200
    assert response.json()["herfindahl_index"] == pytest.approx(1 / 3)


def test_invalid_portfolio_dimensions():
    payload = {
        **PORTFOLIO_PAYLOAD,
        "covariance": [[0.04, 0.01], [0.01, 0.09]],
    }

    response = client.post("/quant/optimize", json=payload)

    assert response.status_code == 400


def test_duplicate_assets():
    payload = {
        **PORTFOLIO_PAYLOAD,
        "assets": ["A", "A", "C"],
    }

    response = client.post("/quant/optimize", json=payload)

    assert response.status_code == 400


def test_invalid_backtest_dimensions():
    payload = {
        "dates": ["2026-01-05", "2026-01-06"],
        "assets": ["A", "B"],
        "prices": [[100, 100]],
        "weights": [0.5, 0.5],
    }

    response = client.post("/quant/backtest", json=payload)

    assert response.status_code == 422
