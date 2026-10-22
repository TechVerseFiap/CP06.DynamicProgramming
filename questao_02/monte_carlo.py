from __future__ import annotations

import random


def monte_carlo_q2(scenarios=2000, seed=14):
    """Simulação básica de demanda, concorrente e custo logístico."""
    random.seed(seed)
    resultado = []
    for _ in range(scenarios):
        demanda = random.uniform(0.9, 1.1)
        concorrente = random.uniform(0.92, 1.08)
        logistica = random.uniform(0.95, 1.15)
        valor = demanda * concorrente * logistica
        resultado.append(valor)
    return sum(resultado) / len(resultado)
