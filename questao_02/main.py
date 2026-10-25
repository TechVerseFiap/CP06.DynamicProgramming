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
    from .dynamic_programming import dynamic_programming_catalog_q2
    from .greedy import greedy_q2
    from .monte_carlo import monte_carlo_q2, validate_q2_policy
except ImportError:  # Supports ``python questao_02/main.py``.
    from dynamic_programming import dynamic_programming_catalog_q2
    from greedy import greedy_q2
    from monte_carlo import monte_carlo_q2, validate_q2_policy


def carregar_catalogo():
    """Load the official generated Q2 catalog; never fall back to sample rows."""
    return load_official_inputs("q2")[0]


def run_q2(items, price_levels, seed, estimate_scenarios, validation_scenarios,
           promotion_budget, debt_schedule, weeks=12, variabilities=None,
           initial_cash=0.0, instance_id=None):
    """Connect Monte Carlo estimation, DP, weekly Greedy, and independent MC."""
    if any(week < 1 or week > weeks or amount < 0 for week, amount in debt_schedule.items()):
        raise ValueError("Debt milestones must be within the horizon and amounts nonnegative")
    estimates = monte_carlo_q2(
        items, price_levels, scenarios=estimate_scenarios, seed=seed, weeks=weeks,
        variabilities=variabilities,
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
        initial_cash=initial_cash,
        variabilities=variabilities,
    )
    return {
        "official_instance_id": instance_id,
        "construction_scenarios": estimate_scenarios,
        "expected_cash_from_dp": round(expected_cash, 2),
        "weekly_policy": weekly_policy,
        "weekly_promotions": promotions,
        "debt_schedule": {str(week): amount for week, amount in debt_schedule.items()},
        "validation": validation,
    }


def main():
    parser = argparse.ArgumentParser(description="Q2 - 12-week survival plan")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--cenarios", type=int, default=None,
                        help="Construction/estimation scenarios (minimum 2000)")
    parser.add_argument("--validacao-cenarios", type=int, default=5000,
                        help="Independent validation scenarios (minimum 5000)")
    args = parser.parse_args()
    items, config, manifest = load_official_inputs("q2")
    estimate_scenarios = (
        args.cenarios if args.cenarios is not None
        else max(2000, config["n_simulacoes_recomendadas"])
    )
    if estimate_scenarios < 2000:
        parser.error("--cenarios must be at least 2000")
    if args.validacao_cenarios < 5000:
        parser.error("--validacao-cenarios must be at least 5000")

    prices = config["niveis_preco_relativos"]
    debt_schedule = {
        int(week.removeprefix("semana_")): amount
        for week, amount in config["dividas"].items()
    }
    seed = args.seed if args.seed is not None else config["seed_final"] + 201
    result = run_q2(
        items,
        prices,
        seed,
        estimate_scenarios,
        args.validacao_cenarios,
        config["orcamento_promocional_semanal"],
        debt_schedule,
        weeks=config["numero_semanas"],
        variabilities=config["variabilidade"],
        initial_cash=config["caixa_inicial"],
        instance_id=manifest["id_instancia"],
    )
    result["estimation_seed"] = seed
    result["validation_seed"] = seed + 1_000_003
    result["debt_risk_limit"] = config["limite_risco_falha"]
    result["variabilities"] = config["variabilidade"]

    output = Path(__file__).resolve().parent / "resultados" / "resultado_q2.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Official instance:", manifest["id_instancia"])
    print("Expected DP cash:", result["expected_cash_from_dp"])
    print("Payment probabilities:", result["validation"]["payment_probability"])
    print("Expected final cash:", result["validation"]["expected_final_cash"])
    print("P10 final cash:", result["validation"]["p10_final_cash"])
    print("Results saved to:", output)


if __name__ == "__main__":
    main()
