from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class BondAnalytics:
    price: float
    yield_to_maturity: float
    macaulay_duration: float
    modified_duration: float
    convexity: float


@dataclass(frozen=True)
class YieldCurve:
    maturities: np.ndarray
    spot_rates: np.ndarray
    discount_factors: np.ndarray


def _validate_positive(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be positive.")


def _validate_non_negative(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be non-negative.")


def _validate_frequency(frequency: int) -> None:
    if not isinstance(frequency, int) or frequency < 1:
        raise ValueError("frequency must be a positive integer.")


def _cashflows(
    face_value: float,
    coupon_rate: float,
    periods: int,
    frequency: int,
) -> np.ndarray:
    coupon = face_value * coupon_rate / frequency
    cashflows = np.full(periods, coupon, dtype=float)
    cashflows[-1] += face_value
    return cashflows


def bond_price(
    face_value: float,
    coupon_rate: float,
    yield_rate: float,
    maturity: float,
    frequency: int = 2,
) -> float:
    _validate_positive("face_value", face_value)
    _validate_non_negative("coupon_rate", coupon_rate)
    if not isinstance(yield_rate, (int, float)):
        raise ValueError("yield_rate must be numeric.")
    _validate_positive("maturity", maturity)
    _validate_frequency(frequency)

    periods_float = maturity * frequency
    periods = round(periods_float)
    if not np.isclose(periods_float, periods):
        raise ValueError("maturity must align with the coupon frequency.")

    cashflows = _cashflows(face_value, coupon_rate, periods, frequency)
    discount_periods = np.arange(1, periods + 1)
    return float(
        np.sum(
            cashflows
            / (1.0 + yield_rate / frequency) ** discount_periods
        )
    )


def bond_yield_to_maturity(
    price: float,
    face_value: float,
    coupon_rate: float,
    maturity: float,
    frequency: int = 2,
) -> float:
    _validate_positive("price", price)
    _validate_positive("face_value", face_value)
    _validate_non_negative("coupon_rate", coupon_rate)
    _validate_positive("maturity", maturity)
    _validate_frequency(frequency)

    def objective(yield_rate: float) -> float:
        return (
            bond_price(
                face_value=face_value,
                coupon_rate=coupon_rate,
                yield_rate=yield_rate,
                maturity=maturity,
                frequency=frequency,
            )
            - price
        )

    lower = -0.99 * frequency
    upper = 10.0

    lower_value = objective(lower)
    upper_value = objective(upper)

    if lower_value * upper_value > 0:
        raise ValueError("Unable to solve yield to maturity.")

    return float(brentq(objective, lower, upper, xtol=1e-12))


def duration(
    face_value: float,
    coupon_rate: float,
    yield_rate: float,
    maturity: float,
    frequency: int = 2,
) -> float:
    _validate_positive("face_value", face_value)
    _validate_non_negative("coupon_rate", coupon_rate)
    if not isinstance(yield_rate, (int, float)):
        raise ValueError("yield_rate must be numeric.")
    _validate_positive("maturity", maturity)
    _validate_frequency(frequency)

    periods_float = maturity * frequency
    periods = round(periods_float)
    if not np.isclose(periods_float, periods):
        raise ValueError("maturity must align with the coupon frequency.")

    cashflows = _cashflows(face_value, coupon_rate, periods, frequency)
    times = np.arange(1, periods + 1, dtype=float) / frequency
    discount_rate = 1.0 + yield_rate / frequency
    present_values = cashflows / discount_rate ** np.arange(1, periods + 1)
    price = float(np.sum(present_values))

    return float(np.sum(times * present_values) / price)


def modified_duration(
    face_value: float,
    coupon_rate: float,
    yield_rate: float,
    maturity: float,
    frequency: int = 2,
) -> float:
    macaulay = duration(
        face_value=face_value,
        coupon_rate=coupon_rate,
        yield_rate=yield_rate,
        maturity=maturity,
        frequency=frequency,
    )
    return float(macaulay / (1.0 + yield_rate / frequency))


def convexity(
    face_value: float,
    coupon_rate: float,
    yield_rate: float,
    maturity: float,
    frequency: int = 2,
) -> float:
    _validate_positive("face_value", face_value)
    _validate_non_negative("coupon_rate", coupon_rate)
    if not isinstance(yield_rate, (int, float)):
        raise ValueError("yield_rate must be numeric.")
    _validate_positive("maturity", maturity)
    _validate_frequency(frequency)

    periods_float = maturity * frequency
    periods = round(periods_float)
    if not np.isclose(periods_float, periods):
        raise ValueError("maturity must align with the coupon frequency.")

    cashflows = _cashflows(face_value, coupon_rate, periods, frequency)
    k = np.arange(1, periods + 1, dtype=float)
    discount_rate = 1.0 + yield_rate / frequency
    present_values = cashflows / discount_rate**k
    price = float(np.sum(present_values))

    convexity_value = np.sum(
        k
        * (k + 1.0)
        * present_values
        / (frequency**2 * discount_rate**2)
    )

    return float(convexity_value / price)


def yield_curve(
    maturities: Sequence[float],
    spot_rates: Sequence[float],
) -> YieldCurve:
    maturities_array = np.asarray(maturities, dtype=float)
    rates_array = np.asarray(spot_rates, dtype=float)

    if maturities_array.ndim != 1 or rates_array.ndim != 1:
        raise ValueError("maturities and spot_rates must be one-dimensional.")
    if len(maturities_array) == 0:
        raise ValueError("Yield curve cannot be empty.")
    if len(maturities_array) != len(rates_array):
        raise ValueError("maturities and spot_rates must have equal lengths.")
    if not np.all(np.isfinite(maturities_array)) or not np.all(
        np.isfinite(rates_array)
    ):
        raise ValueError("Yield curve inputs must be finite.")
    if np.any(maturities_array <= 0):
        raise ValueError("Maturities must be positive.")
    if np.any(np.diff(maturities_array) <= 0):
        raise ValueError("Maturities must be strictly increasing.")

    discount_factors = np.exp(-rates_array * maturities_array)

    return YieldCurve(
        maturities=maturities_array,
        spot_rates=rates_array,
        discount_factors=discount_factors,
    )


def rate_sensitivity(
    price: float,
    modified_duration_value: float,
    convexity_value: float,
    yield_change: float,
) -> float:
    _validate_positive("price", price)
    _validate_non_negative("modified_duration_value", modified_duration_value)
    _validate_non_negative("convexity_value", convexity_value)

    if not isinstance(yield_change, (int, float)):
        raise ValueError("yield_change must be numeric.")

    relative_change = (
        -modified_duration_value * yield_change
        + 0.5 * convexity_value * yield_change**2
    )

    return float(price * (1.0 + relative_change))
