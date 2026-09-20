from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt

from scipy.optimize import brentq


@dataclass(frozen=True)
class ForwardResult:
    forward_price: float


@dataclass(frozen=True)
class FuturesResult:
    futures_price: float


@dataclass(frozen=True)
class GreeksResult:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


@dataclass(frozen=True)
class BlackScholesResult:
    price: float
    greeks: GreeksResult


@dataclass(frozen=True)
class BinomialResult:
    price: float
    steps: int


def _validate_positive(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be positive.")


def _validate_rate(name: str, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric.")


def _validate_option_inputs(
    spot: float,
    strike: float,
    rate: float,
    dividend_yield: float,
    volatility: float,
    time_to_maturity: float,
) -> None:
    _validate_positive("spot", spot)
    _validate_positive("strike", strike)
    _validate_positive("volatility", volatility)
    _validate_positive("time_to_maturity", time_to_maturity)
    _validate_rate("rate", rate)
    _validate_rate("dividend_yield", dividend_yield)


def _normal_pdf(x: float) -> float:
    return exp(-0.5 * x * x) / sqrt(2 * pi)


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def forward_price(
    spot: float,
    rate: float,
    time_to_maturity: float,
    dividend_yield: float = 0.0,
) -> ForwardResult:
    _validate_positive("spot", spot)
    _validate_positive("time_to_maturity", time_to_maturity)
    _validate_rate("rate", rate)
    _validate_rate("dividend_yield", dividend_yield)

    return ForwardResult(
        forward_price=spot * exp((rate - dividend_yield) * time_to_maturity)
    )


def futures_price(
    spot: float,
    rate: float,
    time_to_maturity: float,
    convenience_yield: float = 0.0,
    storage_cost: float = 0.0,
) -> FuturesResult:
    _validate_positive("spot", spot)
    _validate_positive("time_to_maturity", time_to_maturity)
    _validate_rate("rate", rate)
    _validate_rate("convenience_yield", convenience_yield)
    _validate_rate("storage_cost", storage_cost)

    return FuturesResult(
        futures_price=spot
        * exp(
            (rate + storage_cost - convenience_yield)
            * time_to_maturity
        )
    )


def put_call_parity(
    call_price: float,
    spot: float,
    strike: float,
    rate: float,
    time_to_maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    if call_price < 0:
        raise ValueError("call_price must be non-negative.")
    _validate_positive("spot", spot)
    _validate_positive("strike", strike)
    _validate_positive("time_to_maturity", time_to_maturity)
    _validate_rate("rate", rate)
    _validate_rate("dividend_yield", dividend_yield)

    return (
        call_price
        - spot * exp(-dividend_yield * time_to_maturity)
        + strike * exp(-rate * time_to_maturity)
    )


def black_scholes(
    spot: float,
    strike: float,
    rate: float,
    volatility: float,
    time_to_maturity: float,
    option_type: str = "call",
    dividend_yield: float = 0.0,
) -> BlackScholesResult:
    _validate_option_inputs(
        spot,
        strike,
        rate,
        dividend_yield,
        volatility,
        time_to_maturity,
    )

    option_type = option_type.lower()
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")

    sqrt_t = sqrt(time_to_maturity)
    d1 = (
        log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility**2)
        * time_to_maturity
    ) / (volatility * sqrt_t)
    d2 = d1 - volatility * sqrt_t

    discount_rate = exp(-rate * time_to_maturity)
    discount_dividend = exp(-dividend_yield * time_to_maturity)

    call = (
        spot * discount_dividend * _normal_cdf(d1)
        - strike * discount_rate * _normal_cdf(d2)
    )
    put = (
        strike * discount_rate * _normal_cdf(-d2)
        - spot * discount_dividend * _normal_cdf(-d1)
    )

    if option_type == "call":
        price = call
        delta = discount_dividend * _normal_cdf(d1)
        theta = (
            -spot
            * discount_dividend
            * _normal_pdf(d1)
            * volatility
            / (2 * sqrt_t)
            - rate * strike * discount_rate * _normal_cdf(d2)
            + dividend_yield
            * spot
            * discount_dividend
            * _normal_cdf(d1)
        )
        rho = strike * time_to_maturity * discount_rate * _normal_cdf(d2)
    else:
        price = put
        delta = discount_dividend * (_normal_cdf(d1) - 1.0)
        theta = (
            -spot
            * discount_dividend
            * _normal_pdf(d1)
            * volatility
            / (2 * sqrt_t)
            + rate * strike * discount_rate * _normal_cdf(-d2)
            - dividend_yield
            * spot
            * discount_dividend
            * _normal_cdf(-d1)
        )
        rho = -strike * time_to_maturity * discount_rate * _normal_cdf(-d2)

    gamma = (
        discount_dividend * _normal_pdf(d1)
        / (spot * volatility * sqrt_t)
    )
    vega = spot * discount_dividend * _normal_pdf(d1) * sqrt_t

    return BlackScholesResult(
        price=price,
        greeks=GreeksResult(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
        ),
    )


def binomial_option(
    spot: float,
    strike: float,
    rate: float,
    volatility: float,
    time_to_maturity: float,
    option_type: str = "call",
    steps: int = 100,
    dividend_yield: float = 0.0,
    american: bool = False,
) -> BinomialResult:
    _validate_option_inputs(
        spot,
        strike,
        rate,
        dividend_yield,
        volatility,
        time_to_maturity,
    )

    option_type = option_type.lower()
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")
    if not isinstance(steps, int) or steps < 1:
        raise ValueError("steps must be a positive integer.")

    dt = time_to_maturity / steps
    up = exp(volatility * sqrt(dt))
    down = 1.0 / up
    discount = exp(-rate * dt)

    growth = exp((rate - dividend_yield) * dt)
    probability = (growth - down) / (up - down)

    if not 0.0 <= probability <= 1.0:
        raise ValueError("Invalid binomial probability.")

    prices = [
        spot * up**j * down ** (steps - j)
        for j in range(steps + 1)
    ]

    if option_type == "call":
        values = [max(price - strike, 0.0) for price in prices]
    else:
        values = [max(strike - price, 0.0) for price in prices]

    for level in range(steps - 1, -1, -1):
        new_values = []
        for j in range(level + 1):
            continuation = discount * (
                probability * values[j + 1]
                + (1.0 - probability) * values[j]
            )

            if american:
                underlying = spot * up**j * down ** (level - j)
                if option_type == "call":
                    exercise = max(underlying - strike, 0.0)
                else:
                    exercise = max(strike - underlying, 0.0)
                new_values.append(max(continuation, exercise))
            else:
                new_values.append(continuation)

        values = new_values

    return BinomialResult(price=values[0], steps=steps)


def implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    rate: float,
    time_to_maturity: float,
    option_type: str = "call",
    dividend_yield: float = 0.0,
    lower_volatility: float = 1e-6,
    upper_volatility: float = 5.0,
) -> float:
    if market_price < 0:
        raise ValueError("market_price must be non-negative.")
    if lower_volatility <= 0 or upper_volatility <= lower_volatility:
        raise ValueError("Invalid volatility bounds.")

    _validate_option_inputs(
        spot,
        strike,
        rate,
        dividend_yield,
        max(lower_volatility, 1e-8),
        time_to_maturity,
    )

    option_type = option_type.lower()
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")

    def objective(volatility: float) -> float:
        return (
            black_scholes(
                spot=spot,
                strike=strike,
                rate=rate,
                volatility=volatility,
                time_to_maturity=time_to_maturity,
                option_type=option_type,
                dividend_yield=dividend_yield,
            ).price
            - market_price
        )

    lower_value = objective(lower_volatility)
    upper_value = objective(upper_volatility)

    if lower_value == 0:
        return lower_volatility
    if upper_value == 0:
        return upper_volatility
    if lower_value * upper_value > 0:
        raise ValueError("Market price is outside the supported volatility range.")

    return float(
        brentq(
            objective,
            lower_volatility,
            upper_volatility,
            xtol=1e-10,
            rtol=1e-10,
        )
    )
