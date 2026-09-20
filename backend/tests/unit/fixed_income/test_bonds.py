import numpy as np
import pytest

from app.fixed_income.bonds import (
    bond_price,
    bond_yield_to_maturity,
    convexity,
    duration,
    modified_duration,
    rate_sensitivity,
    yield_curve,
)


def test_par_bond_price():
    price = bond_price(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.05,
        maturity=5,
        frequency=2,
    )

    assert price == pytest.approx(1000.0, abs=1e-8)


def test_discount_bond_price():
    price = bond_price(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.06,
        maturity=5,
        frequency=2,
    )

    assert price == pytest.approx(957.349, rel=1e-4)


def test_ytm_recovers_market_yield():
    price = bond_price(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.06,
        maturity=5,
        frequency=2,
    )

    ytm = bond_yield_to_maturity(
        price=price,
        face_value=1000,
        coupon_rate=0.05,
        maturity=5,
        frequency=2,
    )

    assert ytm == pytest.approx(0.06, abs=1e-10)


def test_macaulay_duration():
    value = duration(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.05,
        maturity=5,
        frequency=2,
    )

    assert value == pytest.approx(4.4854328, rel=1e-6)


def test_modified_duration():
    macaulay = duration(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.05,
        maturity=5,
        frequency=2,
    )

    modified = modified_duration(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.05,
        maturity=5,
        frequency=2,
    )

    assert modified == pytest.approx(macaulay / 1.025, rel=1e-10)


def test_convexity_is_positive():
    value = convexity(
        face_value=1000,
        coupon_rate=0.05,
        yield_rate=0.05,
        maturity=5,
        frequency=2,
    )

    assert value > 0


def test_rate_sensitivity():
    price = 1000.0
    modified = 4.3
    convexity_value = 25.0
    yield_change = 0.01

    expected = price * (
        1 - modified * yield_change
        + 0.5 * convexity_value * yield_change**2
    )

    assert rate_sensitivity(
        price,
        modified,
        convexity_value,
        yield_change,
    ) == pytest.approx(expected)


def test_yield_curve_discount_factors():
    result = yield_curve(
        maturities=[1, 2, 5, 10],
        spot_rates=[0.03, 0.035, 0.04, 0.045],
    )

    assert np.allclose(
        result.discount_factors,
        np.exp(
            -np.array([0.03, 0.035, 0.04, 0.045])
            * np.array([1, 2, 5, 10])
        ),
    )


def test_yield_curve_requires_increasing_maturities():
    with pytest.raises(ValueError):
        yield_curve(
            maturities=[1, 5, 3],
            spot_rates=[0.03, 0.04, 0.035],
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"face_value": 0},
        {"maturity": 0},
        {"frequency": 0},
    ],
)
def test_bond_price_rejects_invalid_inputs(kwargs):
    params = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "yield_rate": 0.05,
        "maturity": 5,
        "frequency": 2,
    }
    params.update(kwargs)

    with pytest.raises(ValueError):
        bond_price(**params)


def test_maturity_must_align_with_frequency():
    with pytest.raises(ValueError):
        bond_price(
            face_value=1000,
            coupon_rate=0.05,
            yield_rate=0.05,
            maturity=5.25,
            frequency=2,
        )


def test_rate_sensitivity_rejects_invalid_price():
    with pytest.raises(ValueError):
        rate_sensitivity(
            price=0,
            modified_duration_value=4,
            convexity_value=20,
            yield_change=0.01,
        )
