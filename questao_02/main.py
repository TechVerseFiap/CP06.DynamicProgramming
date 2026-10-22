from __future__ import annotations

import argparse
import json
from pathlib import Path

from dynamic_programming import dynamic_programming_q2
from monte_carlo import monte_carlo_q2
from greedy import greedy_q2


def carregar_catalogo():
    return [
        {
            "sku": "Q2-001",
            "preco_atual": 100.0,
            "estoque_inicial": 25,
            "demanda_base_semanal": 60,
            "elasticidade": 1.2,
            "taxa_marketplace": 0.10,
            "custo_unitario": 50.0,
            "custo_logistico_base": 6.0,
        },
        {
            "sku": "Q2-002",
            "preco_atual": 140.0,
            "estoque_inicial": 30,
            "demanda_base_semanal": 50,
            "elasticidade": 1.0,
            "taxa_marketplace": 0.12,
            "custo_unitario": 80.0,
            "custo_logistico_base": 10.0,
        },
    ]


def main():
    parser = argparse.ArgumentParser(description="Questão 2 — Plano de Sobrevivência em 12 Semanas")
    parser.add_argument("--seed", type=int, default=14)
    parser.add_argument("--cenarios", type=int, default=5000)
    args = parser.parse_args()

    melhor, _ = dynamic_programming_q2(
        demanda_base=60.0,
        elasticidade=1.2,
        estoque_inicial=25,
        preco_base=95.0,
        precos_permitidos=[0.82, 0.88, 0.94, 1.00, 1.06, 1.12],
        custo_unitario=50.0,
        custo_logistico=6.0,
        taxa_marketplace=0.10,
        semanas=12,
    )

    simulacao = monte_carlo_q2(scenarios=args.cenarios, seed=args.seed)
    promocao = greedy_q2(carregar_catalogo(), 150.0)

    resultado = {
        "dp": round(melhor, 2),
        "monte_carlo": round(simulacao, 4),
        "greedy_promocional": round(promocao, 2),
    }

    saida = Path(__file__).resolve().parent / "resultados" / "resultado_q2.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print("DP:", round(melhor, 2))
    print("Monte Carlo:", round(simulacao, 4))
    print("Greedy promocional:", round(promocao, 2))
    print("Arquivo salvo em:", saida)


if __name__ == "__main__":
    main()
