from __future__ import annotations

from itertools import product

try:
    from .metrics import evaluate_policy
except ImportError:  # Supports running main.py directly from the question folder.
    from metrics import evaluate_policy


def brute_force_q1(itens, price_levels, margem_minima):
    """Find the exact best policy by enumerating every price combination."""
    if not price_levels:
        raise ValueError("At least one permitted price multiplier is required")

    # Optimize repeated work: each (SKU, multiplier) contributes the same
    # demand/margin result in every cartesian-product combination.
    outcomes = []
    for item in itens:
        row = {}
        for multiplier in price_levels:
            cash, policy = evaluate_policy([item], [multiplier], margem_minima)
            row[multiplier] = (cash, policy[0])
        outcomes.append(row)

    best_cash = 0.0
    best_policy = []
    for choice in product(price_levels, repeat=len(itens)):
        selected = [outcome[multiplier] for outcome, multiplier in zip(outcomes, choice)]
        cash = sum(entry[0] for entry in selected)
        if cash > best_cash:
            best_cash = cash
            best_policy = [dict(entry[1]) for entry in selected]

    return best_cash, best_policy
