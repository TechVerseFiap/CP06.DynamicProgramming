from __future__ import annotations

import random


DEFAULT_VARIABILITY = {
    "sigma_demanda": 0.12,
    "sigma_preco_concorrente": 0.06,
    "sigma_custo_logistico": 0.10,
}


def _variability_values(variabilities):
    values = {**DEFAULT_VARIABILITY, **(variabilities or {})}
    if any(value < 0 for value in values.values()):
        raise ValueError("Scenario standard deviations cannot be negative")
    return values


def monte_carlo_q2(
    items, price_levels, scenarios=2000, seed=14, weeks=12, variabilities=None
):
    """Estimate weekly demand and unit contribution for each SKU/price.

    Demand, competitor-price movement, and logistics cost are independently
    sampled. The result is an estimation table consumed by the dynamic program.
    """
    if scenarios < 1:
        raise ValueError("scenarios must be at least 1")
    if weeks < 1:
        raise ValueError("weeks must be at least 1")
    if not price_levels or any(multiplier <= 0 for multiplier in price_levels):
        raise ValueError("price_levels must contain positive multipliers")

    rng = random.Random(seed)
    variability = _variability_values(variabilities)
    estimates = {}
    for item in items:
        for multiplier in price_levels:
            price = item["preco_atual"] * multiplier
            for week in range(1, weeks + 1):
                demand_total = 0.0
                margin_total = 0.0
                for _ in range(scenarios):
                    demand_factor = max(0.0, rng.gauss(1.0, variability["sigma_demanda"]))
                    competitor_factor = max(
                        0.01, rng.gauss(1.0, variability["sigma_preco_concorrente"])
                    )
                    logistics_factor = max(
                        0.01, rng.gauss(1.0, variability["sigma_custo_logistico"])
                    )
                    competitor_baseline = (
                        item.get("preco_concorrente_base", item["preco_atual"])
                        / item["preco_atual"]
                    )
                    demand = (
                        item["demanda_base_semanal"]
                        * multiplier ** (-item["elasticidade"])
                        * demand_factor
                        * (competitor_baseline * competitor_factor) ** item["elasticidade"]
                    )
                    unit_margin = (
                        price * (1 - item["taxa_marketplace"])
                        - item["custo_unitario"]
                        - item["custo_logistico_base"] * logistics_factor
                    )
                    demand_total += max(0.0, demand)
                    margin_total += max(0.0, unit_margin)

                estimates[(item["sku"], week, multiplier)] = {
                    "expected_demand": demand_total / scenarios,
                    "expected_unit_margin": margin_total / scenarios,
                }
    return estimates


def validate_q2_policy(
    items,
    weekly_policy,
    promotions,
    debt_schedule,
    scenarios=5000,
    seed=5014,
    initial_cash=0.0,
    variabilities=None,
):
    """Validate a completed policy on independent scenarios and debt dates."""
    if scenarios < 1:
        raise ValueError("scenarios must be at least 1")

    rng = random.Random(seed)
    variability = _variability_values(variabilities)
    items_by_sku = {item["sku"]: item for item in items}
    decisions = {
        (week["week"], entry["sku"]): entry
        for week in weekly_policy
        for entry in week["items"]
    }
    promotion_costs = {
        (entry["week"], allocation["sku"]): allocation["cost"]
        for entry in promotions
        for allocation in entry["allocations"]
    }
    milestones = sorted(debt_schedule)
    final_cash_results = []
    paid_counts = {week: 0 for week in milestones}
    ending_stocks = {sku: [] for sku in items_by_sku}
    failures = []

    for scenario in range(scenarios):
        stocks = {sku: item["estoque_inicial"] for sku, item in items_by_sku.items()}
        cumulative_cash = initial_cash
        total_debt_due = 0.0
        scenario_failures = []

        for week in range(1, max(milestones, default=0) + 1):
            for sku, item in items_by_sku.items():
                cumulative_cash -= promotion_costs.get((week, sku), 0.0)
                decision = decisions.get((week, sku))
                if not decision or stocks[sku] <= 0 or not decision["multiplier"]:
                    continue

                multiplier = decision["multiplier"]
                demand_factor = max(0.0, rng.gauss(1.0, variability["sigma_demanda"]))
                competitor_factor = max(
                    0.01, rng.gauss(1.0, variability["sigma_preco_concorrente"])
                )
                logistics_factor = max(
                    0.01, rng.gauss(1.0, variability["sigma_custo_logistico"])
                )
                competitor_baseline = (
                    item.get("preco_concorrente_base", item["preco_atual"])
                    / item["preco_atual"]
                )
                uplift = 1.10 if (week, sku) in promotion_costs else 1.0
                demand = (
                    item["demanda_base_semanal"]
                    * multiplier ** (-item["elasticidade"])
                    * demand_factor
                    * (competitor_baseline * competitor_factor) ** item["elasticidade"]
                    * uplift
                )
                units = min(stocks[sku], max(0, int(demand)))
                unit_margin = (
                    item["preco_atual"] * multiplier * (1 - item["taxa_marketplace"])
                    - item["custo_unitario"]
                    - item["custo_logistico_base"] * logistics_factor
                )
                if unit_margin > 0:
                    cumulative_cash += units * unit_margin
                    stocks[sku] -= units

            if week in debt_schedule:
                total_debt_due += debt_schedule[week]
                if cumulative_cash >= total_debt_due:
                    paid_counts[week] += 1
                elif len(failures) < 10:
                    scenario_failures.append({
                        "week": week,
                        "cumulative_cash": round(cumulative_cash, 2),
                        "cumulative_debt": round(total_debt_due, 2),
                    })

        final_cash_results.append(cumulative_cash)
        for sku in stocks:
            ending_stocks[sku].append(stocks[sku])
        if scenario_failures and len(failures) < 10:
            failures.append({"scenario": scenario, "missed_obligations": scenario_failures})

    ordered_cash = sorted(final_cash_results)
    percentile_index = int(0.10 * (scenarios - 1))
    return {
        "scenarios": scenarios,
        "validation_seed": seed,
        "payment_probability": {
            str(week): round(paid_counts[week] / scenarios, 4) for week in milestones
        },
        "expected_final_cash": round(sum(final_cash_results) / scenarios, 2),
        "p10_final_cash": round(ordered_cash[percentile_index], 2),
        "mean_ending_stock": {
            sku: round(sum(values) / scenarios, 2)
            for sku, values in ending_stocks.items()
        },
        "failure_examples": failures,
        "final_cash_samples": final_cash_results,
    }
