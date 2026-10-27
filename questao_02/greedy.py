from __future__ import annotations


def greedy_q2(
    items, weekly_policy, budget_per_week, uplift=0.10,
    logistics_cost_multiplier=1.0,
):
    """Allocate weekly promotions by estimated incremental cash per real."""
    if budget_per_week < 0:
        raise ValueError("Weekly promotion budget cannot be negative")
    if uplift < 0:
        raise ValueError("Promotion uplift cannot be negative")
    if logistics_cost_multiplier <= 0:
        raise ValueError("Logistics cost multiplier must be positive")

    items_by_sku = {item["sku"]: item for item in items}
    promotion_plan = []
    for week_plan in weekly_policy:
        candidates = []
        for decision in week_plan["items"]:
            item = items_by_sku[decision["sku"]]
            if decision["multiplier"] is None:
                continue
            extra_demand = int(decision["expected_units"] * uplift)
            extra_units = min(decision["stock_end"], extra_demand)
            unit_cost = max(0.0, item["custo_logistico_base"] * logistics_cost_multiplier)
            cost = extra_units * unit_cost
            price = item["preco_atual"] * decision["multiplier"]
            unit_margin = (
                price * (1 - item["taxa_marketplace"])
                - item["custo_unitario"]
                - item["custo_logistico_base"] * logistics_cost_multiplier
            )
            benefit = extra_units * max(0.0, unit_margin)
            if extra_units and cost > 0 and benefit > cost:
                candidates.append((benefit / cost, item["sku"], extra_units, cost, benefit))

        candidates.sort(key=lambda row: (-row[0], row[1]))
        spent = 0.0
        allocations = []
        for ratio, sku, units, cost, benefit in candidates:
            if cost > budget_per_week - spent:
                continue
            spent += cost
            allocations.append({
                "sku": sku,
                "extra_units": units,
                "cost": round(cost, 2),
                "incremental_cash": round(benefit, 2),
                "benefit_per_real": round(ratio, 4),
            })

        promotion_plan.append({
            "week": week_plan["week"],
            "spent": round(spent, 2),
            "remaining_budget": round(budget_per_week - spent, 2),
            "allocations": allocations,
        })

    return promotion_plan
