from __future__ import annotations


def dynamic_programming_catalog_q2(items, estimates, price_levels, weeks=12):
    """Optimize each SKU over week/stock using Monte Carlo estimates.

    State: (SKU, week, remaining stock). The catalog sample has no cross-SKU
    capacity constraint, so each SKU's independent DP values can be summed.
    """
    if weeks < 1:
        raise ValueError("weeks must be at least 1")
    if not price_levels:
        raise ValueError("At least one permitted price multiplier is required")

    weekly_policy = [{"week": week, "items": []} for week in range(1, weeks + 1)]
    total_cash = 0.0

    for item in items:
        max_stock = item["estoque_inicial"]
        values = [[0.0] * (max_stock + 1) for _ in range(weeks + 1)]
        actions = [[None] * (max_stock + 1) for _ in range(weeks)]

        for week_index in range(weeks - 1, -1, -1):
            week = week_index + 1
            for stock in range(max_stock + 1):
                best_value = values[week_index + 1][stock]
                best_action = None
                for multiplier in price_levels:
                    stats = estimates[(item["sku"], week, multiplier)]
                    units = min(stock, max(0, int(stats["expected_demand"])))
                    if units <= 0:
                        continue
                    remaining = stock - units
                    value = (
                        units * stats["expected_unit_margin"]
                        + values[week_index + 1][remaining]
                    )
                    if value > best_value:
                        best_value = value
                        best_action = multiplier
                values[week_index][stock] = best_value
                actions[week_index][stock] = best_action

        total_cash += values[0][max_stock]
        stock = max_stock
        for week_index in range(weeks):
            multiplier = actions[week_index][stock]
            if multiplier is None:
                weekly_policy[week_index]["items"].append({
                    "sku": item["sku"],
                    "multiplier": None,
                    "expected_units": 0,
                    "stock_start": stock,
                    "stock_end": stock,
                    "expected_cash": 0.0,
                })
                continue

            stats = estimates[(item["sku"], week_index + 1, multiplier)]
            units = min(stock, max(0, int(stats["expected_demand"])))
            remaining = stock - units
            weekly_policy[week_index]["items"].append({
                "sku": item["sku"],
                "multiplier": multiplier,
                "expected_units": units,
                "stock_start": stock,
                "stock_end": remaining,
                "expected_cash": round(units * stats["expected_unit_margin"], 2),
            })
            stock = remaining

    return total_cash, weekly_policy


def dynamic_programming_q2(demanda_base=60.0, elasticidade=1.2, estoque_inicial=25, preco_base=95.0,
                          precos_permitidos=None, custo_unitario=50.0, custo_logistico=6.0,
                          taxa_marketplace=0.10, semanas=12):
    """DP mínima em (semana, estoque)."""
    if precos_permitidos is None:
        precos_permitidos = [0.82, 0.88, 0.94, 1.00, 1.06, 1.12]

    n = semanas + 1
    dp = [[0.0 for _ in range(estoque_inicial + 1)] for _ in range(n)]

    for semana in range(semanas - 1, -1, -1):
        for estoque in range(estoque_inicial + 1):
            melhor = 0.0
            for mult in precos_permitidos:
                preco = preco_base * mult
                demanda = min(estoque, max(0, int(demanda_base * (mult ** (-elasticidade)))))
                if demanda <= 0:
                    continue
                margem = preco * (1.0 - taxa_marketplace) - custo_unitario - custo_logistico
                if margem <= 0:
                    continue
                caixa = demanda * margem
                estoque_restante = max(0, estoque - demanda)
                melhor = max(melhor, caixa + dp[semana + 1][estoque_restante])
            dp[semana][estoque] = melhor

    return dp[0][estoque_inicial], dp
