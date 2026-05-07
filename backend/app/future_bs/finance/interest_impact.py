"""Interest-impact helpers for one-day calendar mismatches."""


def one_day_interest_exposure(principal: float, annual_rate_percent: float, contracts: int = 1) -> float:
    return round(float(principal) * (float(annual_rate_percent) / 100.0) / 365.0 * int(contracts), 2)
