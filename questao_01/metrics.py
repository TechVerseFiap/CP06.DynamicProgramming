from __future__ import annotations


def evaluate_policy(itens, multipliers, margem_minima):
    """Evaluate one price multiplier per SKU using Q1 stock and margin rules."""
    if len(itens) != len(multipliers):
        raise ValueError("Each SKU must have exactly one price multiplier")

    policy = []
    total_cash = 0.0
    for item, multiplier in zip(itens, multipliers):
        if multiplier <= 0:
            raise ValueError("Price multipliers must be positive")

        price = item["preco_atual"] * multiplier
        demand = max(0, int(item["demanda_base_90d"] * multiplier ** (-item["elasticidade"])))
        units = min(item["estoque"], demand)
        unit_margin = (
            price * (1 - item["taxa_marketplace"])
            - item["custo_unitario"]
            - item["custo_logistico"]
        )
        eligible = (
            units > 0
            and unit_margin > 0
            and unit_margin >= item["preco_atual"] * margem_minima
        )
        sold = units if eligible else 0
        cash = sold * unit_margin if eligible else 0.0
        total_cash += cash
        policy.append({
            "sku": item["sku"],
            "multiplier": multiplier,
            "price": round(price, 2),
            "units": sold,
            "unit_margin": round(unit_margin, 2),
            "cash": round(cash, 2),
            "remaining_stock": item["estoque"] - sold,
        })

    return total_cash, policy
