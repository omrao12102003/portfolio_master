from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rl_evaluate_endpoint():
    returns = [
        [0.010, 0.020, 0.015],
        [0.020, 0.010, 0.012],
        [0.000, 0.030, 0.010],
        [0.015, 0.010, 0.014],
        [0.012, 0.018, 0.011],
        [0.008, 0.012, 0.016],
        [0.010, 0.015, 0.013],
        [0.014, 0.011, 0.012],
        [0.009, 0.020, 0.014],
        [0.013, 0.016, 0.010],
    ]

    response = client.post(
        "/rl/evaluate",
        json={
            "returns": returns,
            "assets": ["A", "B", "C"],
            "actions": [
                [1 / 3, 1 / 3, 1 / 3],
                [0.6, 0.2, 0.2],
                [0.2, 0.6, 0.2],
            ],
            "initial_capital": 100_000,
            "transaction_cost_bps": 5,
            "risk_free_rate": 0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["selected_action"] in [0, 1, 2]
    assert len(data["training_rewards"]) == 3

    assert set(data["validation"]) == {
        "final_value",
        "cumulative_return",
        "average_reward",
        "total_turnover",
    }

    assert set(data["test"]) == {
        "final_value",
        "cumulative_return",
        "average_reward",
        "total_turnover",
    }
    assert set(data["q_learning_validation"]) == {
        "final_value",
        "cumulative_return",
        "average_reward",
        "total_turnover",
    }
    assert set(data["q_learning_test"]) == {
        "final_value",
        "cumulative_return",
        "average_reward",
        "total_turnover",
    }

    assert [item["name"] for item in data["strategies"]] == [
        "RL",
        "Equal Weight",
        "Minimum Volatility",
        "Maximum Sharpe",
        "Risk Parity",
    ]


def test_rl_evaluate_rejects_asset_mismatch():
    response = client.post(
        "/rl/evaluate",
        json={
            "returns": [
                [0.01, 0.02, 0.03],
                [0.02, 0.01, 0.02],
                [0.01, 0.03, 0.01],
                [0.02, 0.02, 0.02],
                [0.01, 0.02, 0.01],
                [0.02, 0.01, 0.03],
            ],
            "assets": ["A", "B"],
            "actions": [
                [0.5, 0.5],
                [0.6, 0.4],
            ],
        },
    )

    assert response.status_code == 400
