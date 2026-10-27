from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.official_inputs import load_official_inputs
from questao_01.metrics import apply_promotions

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


def run_q1(
    benchmark_items,
    full_catalog_items,
    price_levels,
    minimum_margin,
    seed,
    promotion_budget,
    ga_configurations=None,
):
    """Connect exact benchmark, GA policy search, and its Greedy allocation."""
    if ga_configurations is None:
        ga_configurations = [
            {"name": "baseline", "population_size": 30, "generations": 50, "mutation_rate": 0.1},
            {"name": "exploration", "population_size": 60, "generations": 100, "mutation_rate": 0.2},
        ]
    benchmark_cash, benchmark_policy = brute_force_q1(
        benchmark_items, price_levels, minimum_margin
    )
    benchmark_ga = genetic_algorithm_q1(
        benchmark_items, price_levels, minimum_margin, seed=seed,
        **{key: value for key, value in ga_configurations[0].items() if key != "name"},
    )
    full_ga_runs = []
    for config in ga_configurations:
        ga_run = genetic_algorithm_q1(
            full_catalog_items,
            price_levels,
            minimum_margin,
            seed=seed,
            **{key: value for key, value in config.items() if key != "name"},
        )
        full_ga_runs.append({"configuration": config, **ga_run})
    full_ga = max(full_ga_runs, key=lambda run: run["cash"])
    promotion = greedy_promocao(
        full_catalog_items, full_ga["policy"], promotion_budget
    )
    post_promotion_policy = apply_promotions(full_ga["policy"], promotion)
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
            "configuration": full_ga["configuration"],
            "policy_before_greedy": full_ga["policy"],
            "policy_after_greedy": post_promotion_policy,
            "fitness_history": full_ga["fitness_history"],
        },
        "ga_comparison": [
            {
                "configuration": run["configuration"],
                "cash": round(run["cash"], 2),
                "fitness_history": run["fitness_history"],
            }
            for run in full_ga_runs
        ],
        "greedy_promotion": promotion,
    }


def main():
    parser = argparse.ArgumentParser(description="Q1 - 90-day cash operation")
    parser.add_argument("--modo", choices=["completo", "benchmark"], default="completo")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--orcamento-promocional", type=float, default=None)
    parser.add_argument("--meta-caixa-multiplicador", type=float, default=1.0)
    parser.add_argument("--remover-sku", action="append", default=[])
    parser.add_argument("--ga-population", type=int, default=30)
    parser.add_argument("--ga-generations", type=int, default=50)
    parser.add_argument("--ga-mutation-rate", type=float, default=0.1)
    parser.add_argument("--ga-alt-population", type=int, default=60)
    parser.add_argument("--ga-alt-generations", type=int, default=100)
    parser.add_argument("--ga-alt-mutation-rate", type=float, default=0.2)
    args = parser.parse_args()

    items, config, manifest = load_official_inputs("q1")
    unknown_skus = set(args.remover_sku) - {item["sku"] for item in items}
    if unknown_skus:
        parser.error("unknown SKU(s): " + ", ".join(sorted(unknown_skus)))
    if args.meta_caixa_multiplicador <= 0:
        parser.error("--meta-caixa-multiplicador must be positive")
    items = [item for item in items if item["sku"] not in set(args.remover_sku)]
    if len(items) < 6:
        parser.error("at least 6 SKUs are required for the exact benchmark")
    seed = args.seed if args.seed is not None else config["seed_final"] + 101
    prices = config["niveis_preco_relativos"]
    minimum_margin = config["margem_minima_percentual"]
    promotion_budget = (
        args.orcamento_promocional
        if args.orcamento_promocional is not None
        else config["orcamento_promocional"]
    )
    full_catalog = items if args.modo == "completo" else items[:6]
    configurations = [
        {"name": "baseline", "population_size": args.ga_population,
         "generations": args.ga_generations, "mutation_rate": args.ga_mutation_rate},
        {"name": "exploration", "population_size": args.ga_alt_population,
         "generations": args.ga_alt_generations,
         "mutation_rate": args.ga_alt_mutation_rate},
    ]
    result = run_q1(
        items[:6], full_catalog, prices, minimum_margin, seed, promotion_budget,
        ga_configurations=configurations,
    )
    full_policy = result["full_catalog_ga"]["policy_after_greedy"]
    promotion = result["greedy_promotion"]
    total_cash = sum(row["cash"] for row in full_policy)
    revenue = sum(row["price"] * row["units"] for row in full_policy)
    total_inventory = sum(item["estoque"] for item in items)
    remaining_inventory = sum(row["remaining_stock"] for row in full_policy)
    target = config["meta_caixa_90d"] * args.meta_caixa_multiplicador
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
    result["greedy_before_after"] = [
        {
            "sku": before["sku"],
            "price": before["price"],
            "units_before": before["units"],
            "cash_before": before["cash"],
            "units_after": after["units"],
            "cash_after_net_of_promotion": after["cash"],
            "inventory_remaining": after["remaining_stock"],
            "promotion_spend": after["promotional_spend"],
        }
        for before, after in zip(
            result["full_catalog_ga"]["policy_before_greedy"], full_policy
        )
    ]
    result["run_mode"] = args.modo
    result["scenario_overrides"] = {
        "meta_caixa_multiplicador": args.meta_caixa_multiplicador,
        "removidos_sku": args.remover_sku,
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
