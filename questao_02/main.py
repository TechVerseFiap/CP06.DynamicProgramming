from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .dynamic_programming import dynamic_programming_catalog_q2
    from .greedy import greedy_q2
    from .monte_carlo import monte_carlo_q2, validate_q2_policy
except ImportError:  # Supports ``python questao_02/main.py``.
    from dynamic_programming import dynamic_programming_catalog_q2
    from greedy import greedy_q2
    from monte_carlo import monte_carlo_q2, validate_q2_policy


def carregar_catalogo():
    """Return illustrative data until official generated inputs are restored."""
    return [
        {
            "sku": "Q2-001", "preco_atual": 100.0, "estoque_inicial": 25,
            "demanda_base_semanal": 60, "elasticidade": 1.2,
            "taxa_marketplace": 0.10, "custo_unitario": 50.0,
            "custo_logistico_base": 6.0,
        },
        {
            "sku": "Q2-002", "preco_atual": 140.0, "estoque_inicial": 30,
            "demanda_base_semanal": 50, "elasticidade": 1.0,
            "taxa_marketplace": 0.12, "custo_unitario": 80.0,
            "custo_logistico_base": 10.0,
        },
    ]


def run_q2(items, price_levels, seed, estimate_scenarios, validation_scenarios,
           promotion_budget, debt_schedule, weeks=12):
    """Connect Monte Carlo estimation, DP, weekly Greedy, and independent MC."""
    if any(week < 1 or week > weeks or amount < 0 for week, amount in debt_schedule.items()):
        raise ValueError("Debt milestones must be within the horizon and amounts nonnegative")
    estimates = monte_carlo_q2(
        items, price_levels, scenarios=estimate_scenarios, seed=seed, weeks=weeks
    )
    expected_cash, weekly_policy = dynamic_programming_catalog_q2(
        items, estimates, price_levels, weeks=weeks
    )
    promotions = greedy_q2(items, weekly_policy, promotion_budget)
    validation = validate_q2_policy(
        items,
        weekly_policy,
        promotions,
        debt_schedule,
        scenarios=validation_scenarios,
        seed=seed + 1_000_003,
    )
    return {
        "sample_data_notice": "Illustrative inputs and debt schedule; not official group data.",
        "construction_scenarios": estimate_scenarios,
        "expected_cash_from_dp": round(expected_cash, 2),
        "weekly_policy": weekly_policy,
        "weekly_promotions": promotions,
        "debt_schedule": {str(week): amount for week, amount in debt_schedule.items()},
        "validation": validation,
    }


def main():
    parser = argparse.ArgumentParser(description="Q2 - 12-week survival plan")
    parser.add_argument("--seed", type=int, default=14)
    parser.add_argument("--cenarios", type=int, default=2000,
                        help="Construction/estimation scenarios (minimum 2000)")
    parser.add_argument("--validacao-cenarios", type=int, default=5000,
                        help="Independent validation scenarios (minimum 5000)")
    parser.add_argument("--orcamento-semanal", type=float, default=150.0)
    parser.add_argument("--divida-semana-4", type=float, default=500.0)
    parser.add_argument("--divida-semana-8", type=float, default=500.0)
    parser.add_argument("--divida-semana-12", type=float, default=500.0)
    args = parser.parse_args()
    if args.cenarios < 2000:
        parser.error("--cenarios must be at least 2000")
    if args.validacao_cenarios < 5000:
        parser.error("--validacao-cenarios must be at least 5000")

    items = carregar_catalogo()
    prices = [0.82, 0.88, 0.94, 1.00, 1.06, 1.12]
    debt_schedule = {
        4: args.divida_semana_4,
        8: args.divida_semana_8,
        12: args.divida_semana_12,
    }
    result = run_q2(
        items,
        prices,
        args.seed,
        args.cenarios,
        args.validacao_cenarios,
        args.orcamento_semanal,
        debt_schedule,
    )
    result["estimation_seed"] = args.seed
    result["validation_seed"] = args.seed + 1_000_003

    output = Path(__file__).resolve().parent / "resultados" / "resultado_q2.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Expected DP cash:", result["expected_cash_from_dp"])
    print("Payment probabilities:", result["validation"]["payment_probability"])
    print("Expected final cash:", result["validation"]["expected_final_cash"])
    print("P10 final cash:", result["validation"]["p10_final_cash"])
    print("Results saved to:", output)


if __name__ == "__main__":
    main()
