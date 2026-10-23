from __future__ import annotations

import random

try:
    from .metrics import evaluate_policy
except ImportError:  # Supports running main.py directly from the question folder.
    from metrics import evaluate_policy


def genetic_algorithm_q1(
    itens,
    price_levels,
    margem_minima,
    population_size=30,
    generations=50,
    mutation_rate=0.1,
    seed=14,
):
    """Search price multipliers with a seeded GA and shared fitness rules."""
    if not price_levels:
        raise ValueError("At least one permitted price multiplier is required")
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    if generations < 1:
        raise ValueError("generations must be at least 1")
    if not 0 <= mutation_rate <= 1:
        raise ValueError("mutation_rate must be between 0 and 1")
    if not itens:
        return {"cash": 0.0, "policy": [], "fitness_history": [], "multipliers": []}

    rng = random.Random(seed)
    population = [
        [rng.choice(price_levels) for _ in itens]
        for _ in range(population_size)
    ]
    history = []
    elite_count = max(1, population_size // 3)

    for _ in range(generations):
        scored = [
            (evaluate_policy(itens, chromosome, margem_minima)[0], chromosome)
            for chromosome in population
        ]
        scored.sort(key=lambda entry: entry[0], reverse=True)
        history.append(round(scored[0][0], 2))
        elites = [chromosome for _, chromosome in scored[:elite_count]]

        next_population = [chromosome[:] for chromosome in elites]
        while len(next_population) < population_size:
            parent_a = rng.choice(elites)
            parent_b = rng.choice(elites)
            child = [
                gene_a if rng.random() < 0.5 else gene_b
                for gene_a, gene_b in zip(parent_a, parent_b)
            ]
            for index in range(len(child)):
                if rng.random() < mutation_rate:
                    child[index] = rng.choice(price_levels)
            next_population.append(child)
        population = next_population

    best_chromosome = max(
        population,
        key=lambda chromosome: evaluate_policy(itens, chromosome, margem_minima)[0],
    )
    best_cash, best_policy = evaluate_policy(itens, best_chromosome, margem_minima)
    history.append(round(best_cash, 2))
    return {
        "cash": best_cash,
        "policy": best_policy,
        "fitness_history": history,
        "multipliers": best_chromosome,
    }
