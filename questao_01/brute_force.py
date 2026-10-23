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

    best_cash = 0.0
    best_policy = []
    for choice in product(price_levels, repeat=len(itens)):
        cash, policy = evaluate_policy(itens, choice, margem_minima)
        if cash > best_cash:
            best_cash, best_policy = cash, policy

    return best_cash, best_policy
