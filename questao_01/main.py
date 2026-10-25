from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.official_inputs import load_official_inputs

try:
    from .brute_force import brute_force_q1
    from .genetic_algorithm import genetic_algorithm_q1
    from .greedy import greedy_promocao
except ImportError:  # Supports ``python questao_01/main.py``.
    from brute_force import brute_force_q1
    from genetic_algorithm import genetic_algorithm_q1
    from greedy import greedy_promocao


def carregar_catalogo():
    """Load the official generated Q1 catalog; never fall back to sample rows."""
    return load_official_inputs("q1")[0]


def run_q1(benchmark_items, full_catalog_items, price_levels, minimum_margin, seed, promotion_budget):
    """Connect exact benchmark, GA policy search, and its Greedy allocation."""
    benchmark_cash, benchmark_policy = brute_force_q1(
        benchmark_items, price_levels, minimum_margin
    )
    benchmark_ga = genetic_algorithm_q1(
        benchmark_items, price_levels, minimum_margin, seed=seed
    )
    full_ga = genetic_algorithm_q1(
        full_catalog_items, price_levels, minimum_margin, seed=seed
    )
    promotion = greedy_promocao(
        full_catalog_items, full_ga["policy"], promotion_budget
    )
    gap = (
        (benchmark_cash - benchmark_ga["cash"]) / benchmark_cash * 100
        if benchmark_cash else 0.0
    )
    return {
        "benchmark": {
            "sku_count": len(benchmark_items),
            "brute_force_cash": round(benchmark_cash, 2),
            "brute_force_policy": benchmark_policy,
            "ga_cash": round(benchmark_ga["cash"], 2),
            "ga_policy": benchmark_ga["policy"],
            "ga_gap_percent": round(gap, 2),
        },
        "full_catalog_ga": {
            "cash": round(full_ga["cash"], 2),
            "policy": full_ga["policy"],
            "fitness_history": full_ga["fitness_history"],
        },
        "greedy_promotion": promotion,
    }


def main():
    parser = argparse.ArgumentParser(description="Q1 - 90-day cash operation")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--orcamento-promocional", type=float, default=None)
    args = parser.parse_args()

    items, config, manifest = load_official_inputs("q1")
    seed = args.seed if args.seed is not None else config["seed_final"] + 101
    prices = config["niveis_preco_relativos"]
    minimum_margin = config["margem_minima_percentual"]
    promotion_budget = (
        args.orcamento_promocional
        if args.orcamento_promocional is not None
        else config["orcamento_promocional"]
    )
    result = run_q1(
        items[:6], items, prices, minimum_margin, seed, promotion_budget
    )
    full_policy = result["full_catalog_ga"]["policy"]
    promotion = result["greedy_promotion"]
    gross_cash = result["full_catalog_ga"]["cash"]
    promo_net = sum(row["incremental_cash"] for row in promotion["allocations"]) - promotion["spent"]
    total_cash = gross_cash + promo_net
    revenue = sum(row["price"] * row["units"] for row in full_policy)
    total_inventory = sum(item["estoque"] for item in items)
    remaining_inventory = sum(row["remaining_stock"] for row in full_policy)
    target = config["meta_caixa_90d"]
    debt = config["divida_total_90d"]
    result["financial_summary"] = {
        "cash_generated_after_promotion_cost": round(total_cash, 2),
        "margin_percent_of_revenue": round(total_cash / revenue, 4) if revenue else 0.0,
        "inventory_total": total_inventory,
        "inventory_remaining": remaining_inventory,
        "cash_target": target,
        "target_attained": total_cash >= target,
        "target_surplus_or_shortfall": round(total_cash - target, 2),
        "debt_total": debt,
        "debt_coverage_ratio": round(total_cash / debt, 4) if debt else None,
        "promotion_budget": promotion_budget,
        "promotion_spent": promotion["spent"],
    }
    result["official_instance"] = {
        "group": manifest["grupo"],
        "seed_base": manifest["seed_base"],
        "seed_final": manifest["seed_final"],
        "instance_id": manifest["id_instancia"],
        "ga_seed": seed,
    }

    output = Path(__file__).resolve().parent / "resultados" / "resultado_q1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Official instance:", result["official_instance"]["instance_id"])
    print("Brute Force (6-SKU benchmark):", result["benchmark"]["brute_force_cash"])
    print("GA benchmark:", result["benchmark"]["ga_cash"])
    print("GA gap (%):", result["benchmark"]["ga_gap_percent"])
    print("Full catalog GA:", result["full_catalog_ga"]["cash"])
    print("Financial summary:", result["financial_summary"])
    print("Greedy promotion:", result["greedy_promotion"])
    print("Results saved to:", output)


if __name__ == "__main__":
    main()
