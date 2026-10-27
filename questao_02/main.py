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
    from .dynamic_programming import (
        dynamic_programming_catalog_q2,
        risk_aware_dynamic_programming_q2,
    )
    from .greedy import greedy_q2
    from .monte_carlo import monte_carlo_q2, validate_q2_policy
except ImportError:  # Supports ``python questao_02/main.py``.
    from dynamic_programming import (
        dynamic_programming_catalog_q2,
        risk_aware_dynamic_programming_q2,
    )
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
    baseline_expected_cash, baseline_policy = dynamic_programming_catalog_q2(
        items, estimates, price_levels, weeks=weeks
    )
    risk_plan = risk_aware_dynamic_programming_q2(
        items, estimates, price_levels, debt_schedule, initial_cash, weeks=weeks
    )
    risk_weekly_policy = risk_plan["weekly_policy"]
    risk_expected_cash = sum(
        decision["expected_cash"]
        for week_plan in risk_weekly_policy
        for decision in week_plan["items"]
    )
    greedy_kwargs = {
        "logistics_cost_multiplier": (variabilities or {}).get(
            "multiplicador_custo_logistico", 1.0
        )
    }
    candidate_specs = [
        {
            "name": "risk_aware_dp",
            "weekly_policy": risk_weekly_policy,
            "state_policy": risk_plan["state_policy"],
            "dp_expected_cash": risk_expected_cash,
        },
        {
            "name": "expected_cash_dp",
            "weekly_policy": baseline_policy,
            "state_policy": None,
            "dp_expected_cash": baseline_expected_cash,
        },
    ]
    candidates = []
    for candidate in candidate_specs:
        candidate_promotions = greedy_q2(
            items, candidate["weekly_policy"], promotion_budget, **greedy_kwargs
        )
        construction_score = validate_q2_policy(
            items,
            candidate["weekly_policy"],
            candidate_promotions,
            debt_schedule,
            scenarios=estimate_scenarios,
            seed=seed + 500_001,
            initial_cash=initial_cash,
            variabilities=variabilities,
            state_policy=candidate["state_policy"],
        )
        candidates.append({
            **candidate,
            "promotions": candidate_promotions,
            "construction_score": {
                "probability_all_obligations_on_time": construction_score[
                    "probability_all_obligations_on_time"
                ],
                "payment_probability": construction_score["payment_probability"],
                "p10_final_cash": construction_score["p10_final_cash"],
                "expected_final_cash": construction_score["expected_final_cash"],
            },
        })
    selected = max(
        candidates,
        key=lambda candidate: (
            candidate["construction_score"]["probability_all_obligations_on_time"],
            candidate["construction_score"]["p10_final_cash"],
            candidate["construction_score"]["expected_final_cash"],
        ),
    )
    weekly_policy = selected["weekly_policy"]
    expected_cash = selected["dp_expected_cash"]
    promotions = selected["promotions"]
    validation = validate_q2_policy(
        items,
        weekly_policy,
        promotions,
        debt_schedule,
        scenarios=validation_scenarios,
        seed=seed + 1_000_003,
        initial_cash=initial_cash,
        variabilities=variabilities,
        state_policy=risk_plan["state_policy"],
    )
    return {
        "official_instance_id": instance_id,
        "construction_scenarios": estimate_scenarios,
        "expected_cash_from_dp": round(expected_cash, 2),
        "baseline_expected_cash_dp": round(baseline_expected_cash, 2),
        "policy_selection_objective": "Maximize construction-scenario probability of meeting all debt deadlines; break ties by P10 then expected cash.",
        "candidate_policy_scores": [
            {"name": candidate["name"], **candidate["construction_score"]}
            for candidate in candidates
        ],
        "selected_policy": selected["name"],
        "risk_aware_dp": {
            key: value for key, value in risk_plan.items()
            if key not in {"weekly_policy", "state_policy"}
        },
        "baseline_expected_cash_policy": baseline_policy,
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
    parser.add_argument("--reducao-concorrente", type=float, default=0.0,
                        help="Competitor price shock, e.g. -0.08 for an 8%% reduction")
    parser.add_argument("--multiplicador-custo-logistico", type=float, default=1.0)
    parser.add_argument("--multiplicador-orcamento", type=float, default=1.0)
    parser.add_argument("--multiplicador-divida", type=float, default=1.0)
    parser.add_argument("--remover-sku", action="append", default=[])
    args = parser.parse_args()
    items, config, manifest = load_official_inputs("q2")
    unknown_skus = set(args.remover_sku) - {item["sku"] for item in items}
    if unknown_skus:
        parser.error("unknown SKU(s): " + ", ".join(sorted(unknown_skus)))
    items = [item for item in items if item["sku"] not in set(args.remover_sku)]
    if not items:
        parser.error("at least one SKU must remain available")
    if args.multiplicador_custo_logistico <= 0:
        parser.error("--multiplicador-custo-logistico must be positive")
    if args.multiplicador_orcamento < 0 or args.multiplicador_divida < 0:
        parser.error("budget and debt multipliers cannot be negative")
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
        int(week.removeprefix("semana_")): amount * args.multiplicador_divida
        for week, amount in config["dividas"].items()
    }
    variabilities = dict(config["variabilidade"])
    variabilities["shift_preco_concorrente"] = args.reducao_concorrente
    variabilities["multiplicador_custo_logistico"] = args.multiplicador_custo_logistico
    seed = args.seed if args.seed is not None else config["seed_final"] + 201
    result = run_q2(
        items,
        prices,
        seed,
        estimate_scenarios,
        args.validacao_cenarios,
        config["orcamento_promocional_semanal"] * args.multiplicador_orcamento,
        debt_schedule,
        weeks=config["numero_semanas"],
        variabilities=variabilities,
        initial_cash=config["caixa_inicial"],
        instance_id=manifest["id_instancia"],
    )
    result["estimation_seed"] = seed
    result["validation_seed"] = seed + 1_000_003
    result["debt_risk_limit"] = config["limite_risco_falha"]
    result["variabilities"] = variabilities
    result["scenario_overrides"] = {
        "reducao_concorrente": args.reducao_concorrente,
        "multiplicador_custo_logistico": args.multiplicador_custo_logistico,
        "multiplicador_orcamento": args.multiplicador_orcamento,
        "multiplicador_divida": args.multiplicador_divida,
        "removidos_sku": args.remover_sku,
    }

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
