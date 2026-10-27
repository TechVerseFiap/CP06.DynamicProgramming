from __future__ import annotations

import csv
import json
import sys
import time
import tracemalloc
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.official_inputs import load_official_inputs
from questao_01.brute_force import brute_force_q1
from questao_01.genetic_algorithm import genetic_algorithm_q1
from questao_01.greedy import greedy_promocao
from questao_01.metrics import evaluate_policy
from questao_02.dynamic_programming import (
    dynamic_programming_catalog_q2,
    risk_aware_dynamic_programming_q2,
)
from questao_02.greedy import greedy_q2
from questao_02.monte_carlo import monte_carlo_q2, validate_q2_policy


def measure(callable_):
    tracemalloc.start()
    start = time.perf_counter()
    result = callable_()
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / (1024 * 1024)


def brute_force_reference(items, levels, margin_floor):
    best = 0.0
    best_policy = []
    for multipliers in product(levels, repeat=len(items)):
        cash, policy = evaluate_policy(items, multipliers, margin_floor)
        if cash > best:
            best, best_policy = cash, policy
    return best, best_policy


def _record(rows, algorithm, size, elapsed, peak, scenarios="", weeks="", prices="", details=""):
    rows.append({
        "algorithm": algorithm,
        "input_size_skus": size,
        "scenarios": scenarios,
        "weeks": weeks,
        "price_levels": prices,
        "elapsed_seconds": round(elapsed, 6),
        "peak_memory_mib": round(peak, 4),
        "notes": details,
    })


def _write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "algorithm", "input_size_skus", "scenarios", "weeks", "price_levels",
        "elapsed_seconds", "peak_memory_mib", "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def benchmark_q1():
    items, config, manifest = load_official_inputs("q1")
    levels = config["niveis_preco_relativos"]
    floor = config["margem_minima_percentual"]
    seed = config["seed_final"] + 101
    rows = []

    for size in (3, 4, 6):
        subset = items[:size]
        reference, elapsed, peak = measure(
            lambda: brute_force_reference(subset, levels, floor)
        )
        _record(rows, "Brute Force reference", size, elapsed, peak,
                prices=len(levels), details=f"cash={reference[0]:.2f}; unoptimized repeated evaluation")
        optimized, elapsed, peak = measure(
            lambda: brute_force_q1(subset, levels, floor)
        )
        if abs(reference[0] - optimized[0]) > 0.01:
            raise AssertionError("Optimized Brute Force differs from reference result")
        _record(rows, "Brute Force optimized", size, elapsed, peak,
                prices=len(levels), details=f"cash={optimized[0]:.2f}; equivalent to reference")

    base_ga = {"population_size": 30, "generations": 50, "mutation_rate": 0.1}
    for size in (3, 15, 30):
        subset = items[:size]
        ga, elapsed, peak = measure(
            lambda: genetic_algorithm_q1(subset, levels, floor, seed=seed, **base_ga)
        )
        _record(rows, "Genetic Algorithm", size, elapsed, peak, prices=len(levels),
                details=f"seed={seed}; cash={ga['cash']:.2f}; K=30,G=50,mutation=0.1")
        _, policy = ga["cash"], ga["policy"]
        promotion, elapsed, peak = measure(
            lambda: greedy_promocao(subset, policy, config["orcamento_promocional"])
        )
        _record(rows, "Greedy", size, elapsed, peak,
                details=f"allocated={len(promotion['allocations'])}; spend={promotion['spent']:.2f}")

    full_rows = []
    for settings in (
        {"name": "baseline", "population_size": 30, "generations": 50, "mutation_rate": 0.1},
        {"name": "exploration", "population_size": 60, "generations": 100, "mutation_rate": 0.2},
    ):
        args = {key: value for key, value in settings.items() if key != "name"}
        run, elapsed, peak = measure(
            lambda: genetic_algorithm_q1(items, levels, floor, seed=seed, **args)
        )
        full_rows.append({
            "configuration": settings["name"],
            "population_size": settings["population_size"],
            "generations": settings["generations"],
            "mutation_rate": settings["mutation_rate"],
            "cash": round(run["cash"], 2),
            "elapsed_seconds": round(elapsed, 6),
            "peak_memory_mib": round(peak, 4),
            "instance_id": manifest["id_instancia"],
        })
    output = ROOT / "questao_01" / "resultados"
    _write_csv(output / "performance.csv", rows)
    with (output / "ga_config_performance.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(full_rows[0]))
        writer.writeheader()
        writer.writerows(full_rows)
    return rows


def benchmark_q2():
    items, config, manifest = load_official_inputs("q2")
    levels = config["niveis_preco_relativos"]
    weeks = config["numero_semanas"]
    scenarios = max(2000, config["n_simulacoes_recomendadas"])
    seed = config["seed_final"] + 201
    variabilities = config["variabilidade"]
    debt_schedule = {
        int(name.removeprefix("semana_")): amount
        for name, amount in config["dividas"].items()
    }
    rows = []

    for size in (3, 12, 24):
        subset = items[:size]
        estimates, elapsed, peak = measure(
            lambda: monte_carlo_q2(
                subset, levels, scenarios=scenarios, seed=seed, weeks=weeks,
                variabilities=variabilities,
            )
        )
        _record(rows, "Monte Carlo estimation", size, elapsed, peak,
                scenarios=scenarios, weeks=weeks, prices=len(levels),
                details=f"seed={seed}; instance={manifest['id_instancia']}")
        risk, elapsed, peak = measure(
            lambda: risk_aware_dynamic_programming_q2(
                subset, estimates, levels, debt_schedule,
                config["caixa_inicial"], weeks=weeks,
            )
        )
        policy = risk["weekly_policy"]
        _record(rows, "Risk-aware DP", size, elapsed, peak,
                weeks=weeks, prices=len(levels),
                details=f"objective={risk['expected_on_time_debt_fraction']:.6f}")
        promotions, elapsed, peak = measure(
            lambda: greedy_q2(
                subset, policy, config["orcamento_promocional_semanal"],
                logistics_cost_multiplier=1.0,
            )
        )
        _record(rows, "Greedy", size, elapsed, peak, weeks=weeks,
                details=f"campaigns={sum(len(row['allocations']) for row in promotions)}")
        _, elapsed, peak = measure(
            lambda: validate_q2_policy(
                subset, policy, promotions, debt_schedule, scenarios=5000,
                seed=seed + 1_000_003, initial_cash=config["caixa_inicial"],
                variabilities=variabilities, state_policy=risk["state_policy"],
            )
        )
        _record(rows, "Monte Carlo validation", size, elapsed, peak,
                scenarios=5000, weeks=weeks,
                details=f"independent seed={seed + 1_000_003}")
        _write_csv(ROOT / "questao_02" / "resultados" / "performance.csv", rows)

    output = ROOT / "questao_02" / "resultados" / "performance.csv"
    _write_csv(output, rows)
    return rows


def main():
    q1 = benchmark_q1()
    q2 = benchmark_q2()
    print(f"Q1 measurements: {len(q1)} rows")
    print(f"Q2 measurements: {len(q2)} rows")
    print("Wrote questao_01/resultados/performance.csv and questao_02/resultados/performance.csv")


if __name__ == "__main__":
    main()
