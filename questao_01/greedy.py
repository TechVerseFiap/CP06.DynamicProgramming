from __future__ import annotations


def greedy_promocao(itens, politica, orcamento_promocional, uplift=0.10):
    """Allocate promotions by incremental contribution per real spent.

    This sample model assumes ``uplift`` additional demand and uses each SKU's
    logistics cost as the per-unit promotional cost. Replace these assumptions
    with official configuration when it becomes available.
    """
    if orcamento_promocional < 0:
        raise ValueError("Promotion budget cannot be negative")
    if uplift < 0:
        raise ValueError("Promotion uplift cannot be negative")

    policy_by_sku = {entry["sku"]: entry for entry in politica}
    candidates = []
    for item in itens:
        baseline = policy_by_sku.get(item["sku"])
        if baseline is None or baseline["units"] <= 0:
            continue

        extra_demand = int(baseline["units"] * uplift)
        extra_units = min(
            max(0, item["estoque"] - baseline["units"]), extra_demand
        )
        unit_cost = max(0.0, item["custo_logistico"])
        cost = extra_units * unit_cost
        benefit = extra_units * baseline["unit_margin"]
        if extra_units and cost > 0:
            candidates.append((benefit / cost, item["sku"], extra_units, cost, benefit))

    candidates.sort(key=lambda entry: (-entry[0], entry[1]))
    spent = 0.0
    allocations = []
    for ratio, sku, units, cost, benefit in candidates:
        if cost > orcamento_promocional - spent:
            continue
        spent += cost
        allocations.append({
            "sku": sku,
            "extra_units": units,
            "cost": round(cost, 2),
            "incremental_cash": round(benefit, 2),
            "benefit_per_real": round(ratio, 4),
        })

    return {
        "spent": round(spent, 2),
        "remaining_budget": round(orcamento_promocional - spent, 2),
        "allocations": allocations,
    }
