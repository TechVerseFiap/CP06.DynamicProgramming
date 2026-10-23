from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .brute_force import brute_force_q1
    from .genetic_algorithm import genetic_algorithm_q1
    from .greedy import greedy_promocao
except ImportError:  # Supports ``python questao_01/main.py``.
    from brute_force import brute_force_q1
    from genetic_algorithm import genetic_algorithm_q1
    from greedy import greedy_promocao


def carregar_catalogo():
    """Return an illustrative catalog until official generated data is available."""
    return [
        {"sku": "Q1-001", "preco_atual": 120.0, "estoque": 18,
         "demanda_base_90d": 35, "elasticidade": 1.3, "taxa_marketplace": 0.10,
         "custo_unitario": 60.0, "custo_logistico": 8.0},
        {"sku": "Q1-002", "preco_atual": 90.0, "estoque": 25,
         "demanda_base_90d": 42, "elasticidade": 1.1, "taxa_marketplace": 0.08,
         "custo_unitario": 45.0, "custo_logistico": 7.0},
        {"sku": "Q1-003", "preco_atual": 300.0, "estoque": 12,
         "demanda_base_90d": 18, "elasticidade": 1.5, "taxa_marketplace": 0.12,
         "custo_unitario": 150.0, "custo_logistico": 20.0},
        {"sku": "Q1-004", "preco_atual": 75.0, "estoque": 40,
         "demanda_base_90d": 55, "elasticidade": 1.0, "taxa_marketplace": 0.09,
         "custo_unitario": 35.0, "custo_logistico": 6.0},
        {"sku": "Q1-005", "preco_atual": 210.0, "estoque": 16,
         "demanda_base_90d": 24, "elasticidade": 1.4, "taxa_marketplace": 0.11,
         "custo_unitario": 105.0, "custo_logistico": 14.0},
        {"sku": "Q1-006", "preco_atual": 55.0, "estoque": 50,
         "demanda_base_90d": 70, "elasticidade": 0.9, "taxa_marketplace": 0.07,
         "custo_unitario": 25.0, "custo_logistico": 5.0},
    ]


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
    parser.add_argument("--seed", type=int, default=14)
    parser.add_argument("--orcamento-promocional", type=float, default=250.0)
    args = parser.parse_args()

    items = carregar_catalogo()
    prices = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10]
    result = run_q1(items[:6], items, prices, 0.05, args.seed, args.orcamento_promocional)
    result["sample_data_notice"] = (
        "Illustrative sample catalog; replace with official generated inputs."
    )
    result["seed"] = args.seed

    output = Path(__file__).resolve().parent / "resultados" / "resultado_q1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Brute Force (6-SKU benchmark):", result["benchmark"]["brute_force_cash"])
    print("GA benchmark:", result["benchmark"]["ga_cash"])
    print("GA gap (%):", result["benchmark"]["ga_gap_percent"])
    print("Full catalog GA:", result["full_catalog_ga"]["cash"])
    print("Greedy promotion:", result["greedy_promotion"])
    print("Results saved to:", output)


if __name__ == "__main__":
    main()
