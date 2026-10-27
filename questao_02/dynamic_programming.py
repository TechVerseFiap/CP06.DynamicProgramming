from __future__ import annotations


def risk_aware_dynamic_programming_q2(
    items, estimates, price_levels, debt_schedule, initial_cash, weeks=12, cash_bins=10
):
    """Choose a policy maximizing expected debt paid on time (discretized DP).

    State per SKU is (week, remaining stock, cash bucket). Debt and initial cash
    are allocated across SKUs in proportion to each SKU's estimated base-price
    contribution. The objective is the expected fraction of scheduled debt
    obligations met by their deadlines. Portfolio payment probabilities are
    measured separately by the independent Monte Carlo validator.
    """
    if weeks < 1 or cash_bins < 1:
        raise ValueError("weeks and cash_bins must be positive")
    if not price_levels:
        raise ValueError("At least one permitted price multiplier is required")
    if initial_cash < 0 or any(amount < 0 for amount in debt_schedule.values()):
        raise ValueError("Cash and debt amounts cannot be negative")
    if any(week < 1 or week > weeks for week in debt_schedule):
        raise ValueError("Debt milestones must fall within the planning horizon")

    base_multiplier = min(price_levels, key=lambda value: abs(value - 1.0))
    contribution_basis = {}
    for item in items:
        stock = item["estoque_inicial"]
        potential = 0.0
        for week in range(1, weeks + 1):
            stats = estimates[(item["sku"], week, base_multiplier)]
            units = min(stock, max(0, int(stats["expected_demand"])))
            potential += units * stats["expected_unit_margin"]
            stock -= units
        contribution_basis[item["sku"]] = max(0.0, potential)
    basis_total = sum(contribution_basis.values())
    if basis_total == 0:
        shares = {item["sku"]: 1 / len(items) for item in items} if items else {}
    else:
        shares = {sku: amount / basis_total for sku, amount in contribution_basis.items()}

    cumulative_debt = {}
    running_debt = 0.0
    for week in range(1, weeks + 1):
        running_debt += debt_schedule.get(week, 0.0)
        cumulative_debt[week] = running_debt
    total_debt = sum(debt_schedule.values())
    weekly_policy = [{"week": week, "items": []} for week in range(1, weeks + 1)]
    objective_value = 0.0
    policy_tables = {}
    cash_bin_sizes = {}

    for item in items:
        sku = item["sku"]
        share = shares[sku]
        target_cash = total_debt * share
        bin_size = max(1.0, target_cash / cash_bins)
        max_cash_bin = cash_bins
        max_stock = item["estoque_inicial"]
        next_values = [[0.0] * (max_cash_bin + 1) for _ in range(max_stock + 1)]
        actions = [
            [[None] * (max_cash_bin + 1) for _ in range(max_stock + 1)]
            for _ in range(weeks)
        ]
        policy_tables[sku] = actions
        cash_bin_sizes[sku] = bin_size

        for week_index in range(weeks - 1, -1, -1):
            week = week_index + 1
            current_values = [[0.0] * (max_cash_bin + 1) for _ in range(max_stock + 1)]
            deadline_weight = (
                debt_schedule.get(week, 0.0) * share / total_debt
                if total_debt > 0 else 0.0
            )
            allocated_target = cumulative_debt[week] * share
            for stock in range(max_stock + 1):
                for cash_bin in range(max_cash_bin + 1):
                    cash_lower_bound = cash_bin * bin_size
                    best_value = -1.0
                    best_action = None
                    actions_for_week = [None, *price_levels]
                    for multiplier in actions_for_week:
                        if multiplier is None:
                            outcomes = [{
                                "probability": 1.0,
                                "demand_units": 0,
                                "unit_margin": 0.0,
                            }]
                        else:
                            outcomes = estimates[(sku, week, multiplier)].get("outcomes")
                            if not outcomes:
                                stats = estimates[(sku, week, multiplier)]
                                outcomes = [{
                                    "probability": 1.0,
                                    "demand_units": int(stats["expected_demand"]),
                                    "unit_margin": stats["expected_unit_margin"],
                                }]

                        expected_value = 0.0
                        for outcome in outcomes:
                            sold = min(stock, max(0, outcome["demand_units"]))
                            earned = sold * max(0.0, outcome["unit_margin"])
                            next_stock = stock - sold
                            next_cash_bin = min(
                                max_cash_bin,
                                int((cash_lower_bound + earned) / bin_size),
                            )
                            deadline_reward = (
                                deadline_weight
                                if cash_bin * bin_size + earned >= allocated_target
                                else 0.0
                            )
                            expected_value += outcome["probability"] * (
                                deadline_reward + next_values[next_stock][next_cash_bin]
                            )
                        if expected_value > best_value:
                            best_value = expected_value
                            best_action = multiplier
                    current_values[stock][cash_bin] = max(0.0, best_value)
                    actions[week_index][stock][cash_bin] = best_action
            next_values = current_values

        initial_cash_share = initial_cash * share
        cash_bin = min(max_cash_bin, int(initial_cash_share / bin_size))
        stock = max_stock
        objective_value += next_values[stock][cash_bin]
        accumulated_cash = initial_cash_share
        for week_index in range(weeks):
            week = week_index + 1
            multiplier = actions[week_index][stock][cash_bin]
            if multiplier is None:
                expected_units = 0
                expected_margin = 0.0
            else:
                stats = estimates[(sku, week, multiplier)]
                expected_units = min(stock, max(0, int(stats["expected_demand"])))
                expected_margin = stats["expected_unit_margin"]
            remaining = stock - expected_units
            earned = expected_units * expected_margin
            weekly_policy[week_index]["items"].append({
                "sku": sku,
                "multiplier": multiplier,
                "expected_units": expected_units,
                "stock_start": stock,
                "stock_end": remaining,
                "expected_cash": round(earned, 2),
                "cash_bucket_start": cash_bin,
            })
            accumulated_cash += earned
            cash_bin = min(max_cash_bin, int(accumulated_cash / bin_size))
            stock = remaining

    return {
        "expected_on_time_debt_fraction": round(objective_value, 6),
        "debt_share_by_sku": shares,
        "weekly_policy": weekly_policy,
        "state_policy": {
            "actions": policy_tables,
            "cash_bin_sizes": cash_bin_sizes,
            "shares": shares,
            "max_cash_bin": cash_bins,
        },
        "cash_bucket_count_per_sku": cash_bins + 1,
        "cash_bucket_resolution_note": "Cash is rounded down to conservative per-SKU buckets.",
    }


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
