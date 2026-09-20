import math

import pytest

from app.derivatives.pricing import (
    binomial_option,
    black_scholes,
    forward_price,
    futures_price,
    implied_volatility,
    put_call_parity,
)


def test_forward_price():
    result = forward_price(100.0, 0.05, 1.0)
    assert result.forward_price == pytest.approx(105.1271, rel=1e-4)


def test_forward_with_dividend_yield():
    result = forward_price(100.0, 0.05, 1.0, dividend_yield=0.02)
    assert result.forward_price == pytest.approx(103.0455, rel=1e-4)


def test_futures_price():
    result = futures_price(100.0, 0.05, 1.0)
    assert result.futures_price == pytest.approx(105.1271, rel=1e-4)


def test_futures_with_carry_inputs():
    result = futures_price(
        100.0,
        0.05,
        1.0,
        convenience_yield=0.02,
        storage_cost=0.01,
    )
    assert result.futures_price == pytest.approx(104.0811, rel=1e-4)


def test_put_call_parity():
    call = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
    ).price

    put = put_call_parity(
        call_price=call,
        spot=100,
        strike=100,
        rate=0.05,
        time_to_maturity=1,
    )

    expected_put = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
        option_type="put",
    ).price

    assert put == pytest.approx(expected_put, rel=1e-10)


def test_black_scholes_call():
    result = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
    )

    assert result.price == pytest.approx(10.4506, rel=1e-4)
    assert result.greeks.delta == pytest.approx(0.6368, rel=1e-3)
    assert result.greeks.gamma == pytest.approx(0.01876, rel=1e-3)
    assert result.greeks.vega == pytest.approx(37.524, rel=1e-3)


def test_black_scholes_put():
    result = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
        option_type="put",
    )

    assert result.price == pytest.approx(5.5735, rel=1e-4)
    assert result.greeks.delta == pytest.approx(-0.3632, rel=1e-3)
    assert result.greeks.rho == pytest.approx(-41.8905, rel=1e-3)


def test_black_scholes_dividend():
    result = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
        dividend_yield=0.02,
    )

    assert result.price == pytest.approx(9.2270, rel=1e-3)


def test_binomial_converges_to_black_scholes():
    bs = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
    ).price

    tree = binomial_option(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
        steps=200,
    ).price

    assert tree == pytest.approx(bs, abs=0.08)


def test_american_put_not_below_european_put():
    european = binomial_option(
        spot=100,
        strike=110,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
        option_type="put",
        steps=100,
        american=False,
    ).price

    american = binomial_option(
        spot=100,
        strike=110,
        rate=0.05,
        volatility=0.20,
        time_to_maturity=1,
        option_type="put",
        steps=100,
        american=True,
    ).price

    assert american >= european


def test_implied_volatility_recovers_input():
    market_price = black_scholes(
        spot=100,
        strike=100,
        rate=0.05,
        volatility=0.25,
        time_to_maturity=1,
    ).price

    implied = implied_volatility(
        market_price=market_price,
        spot=100,
        strike=100,
        rate=0.05,
        time_to_maturity=1,
    )

    assert implied == pytest.approx(0.25, abs=1e-8)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"spot": 0},
        {"strike": 0},
        {"volatility": 0},
        {"time_to_maturity": 0},
    ],
)
def test_black_scholes_rejects_invalid_inputs(kwargs):
    params = {
        "spot": 100,
        "strike": 100,
        "rate": 0.05,
        "volatility": 0.20,
        "time_to_maturity": 1,
    }
    params.update(kwargs)

    with pytest.raises(ValueError):
        black_scholes(**params)


def test_black_scholes_rejects_invalid_option():
    with pytest.raises(ValueError):
        black_scholes(
            spot=100,
            strike=100,
            rate=0.05,
            volatility=0.2,
            time_to_maturity=1,
            option_type="invalid",
        )


def test_binomial_rejects_invalid_steps():
    with pytest.raises(ValueError):
        binomial_option(
            spot=100,
            strike=100,
            rate=0.05,
            volatility=0.2,
            time_to_maturity=1,
            steps=0,
        )


def test_implied_volatility_rejects_unreachable_price():
    with pytest.raises(ValueError):
        implied_volatility(
            market_price=1000,
            spot=100,
            strike=100,
            rate=0.05,
            time_to_maturity=1,
        )


def test_black_scholes_greeks_are_finite():
    result = black_scholes(
        spot=120,
        strike=110,
        rate=0.04,
        volatility=0.30,
        time_to_maturity=0.75,
        option_type="call",
    )

    values = [
        result.price,
        result.greeks.delta,
        result.greeks.gamma,
        result.greeks.theta,
        result.greeks.vega,
        result.greeks.rho,
    ]

    assert all(math.isfinite(value) for value in values)
