from __future__ import annotations

import random


def genetic_algorithm_q1(itens, price_levels, margem_minima, population_size=30, generations=50, mutation_rate=0.1):
    """Versão enxuta do GA para a questão 1."""
    random.seed(14)

    population = []
    for _ in range(population_size):
        chromosome = [random.choice(price_levels) for _ in itens]
        population.append(chromosome)

    for _ in range(generations):
        scored = []
        for chrom in population:
            caixa = 0.0
            for item, mult in zip(itens, chrom):
                preco = item["preco_atual"] * mult
                demanda = min(item["estoque"], max(0, int(item["demanda_base_90d"] * (mult ** (-item["elasticidade"])))) )
                margem = preco * (1 - item["taxa_marketplace"]) - item["custo_unitario"] - item["custo_logistico"]
                if demanda > 0 and margem > 0 and margem >= item["preco_atual"] * margem_minima:
                    caixa += demanda * margem
            scored.append((caixa, chrom))

        scored.sort(key=lambda x: x[0], reverse=True)
        elites = [chrom for _, chrom in scored[: max(1, population_size // 3)]]

        new_population = elites[:]
        while len(new_population) < population_size:
            parent_a = random.choice(elites)
            parent_b = random.choice(elites)
            child = []
            for a, b in zip(parent_a, parent_b):
                child.append(a if random.random() < 0.5 else b)
            if random.random() < mutation_rate:
                idx = random.randrange(len(child))
                child[idx] = random.choice(price_levels)
            new_population.append(child)

        population = new_population

    best = max(population, key=lambda chrom: sum(
        min(item["estoque"], max(0, int(item["demanda_base_90d"] * (mult ** (-item["elasticidade"])))) ) *
        (item["preco_atual"] * mult * (1 - item["taxa_marketplace"]) - item["custo_unitario"] - item["custo_logistico"])
        for item, mult in zip(itens, chrom)
        if item["preco_atual"] * mult * (1 - item["taxa_marketplace"]) - item["custo_unitario"] - item["custo_logistico"] > 0
    ))

    return best
