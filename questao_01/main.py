from __future__ import annotations

import argparse
import json
from pathlib import Path

from brute_force import brute_force_q1
from genetic_algorithm import genetic_algorithm_q1
from greedy import greedy_promocao


def carregar_catalogo():
    return [
        {
            "sku": "Q1-001",
            "preco_atual": 120.0,
            "estoque": 18,
            "demanda_base_90d": 35,
            "elasticidade": 1.3,
            "taxa_marketplace": 0.10,
            "custo_unitario": 60.0,
            "custo_logistico": 8.0,
        },
        {
            "sku": "Q1-002",
            "preco_atual": 90.0,
            "estoque": 25,
            "demanda_base_90d": 42,
            "elasticidade": 1.1,
            "taxa_marketplace": 0.08,
            "custo_unitario": 45.0,
            "custo_logistico": 7.0,
        },
        {
            "sku": "Q1-003",
            "preco_atual": 300.0,
            "estoque": 12,
            "demanda_base_90d": 18,
            "elasticidade": 1.5,
            "taxa_marketplace": 0.12,
            "custo_unitario": 150.0,
            "custo_logistico": 20.0,
        },
    ]


def main():
    parser = argparse.ArgumentParser(description="Questão 1 — Operação Caixa 90")
    parser.add_argument("--modo", choices=["completo", "benchmark"], default="completo")
    args = parser.parse_args()

    itens = carregar_catalogo()
    price_levels = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10]
    margem_minima = 0.05

    bf_valor, bf_decisao = brute_force_q1(itens[:3], price_levels, margem_minima)
    ga = genetic_algorithm_q1(itens[:3], price_levels, margem_minima)
    gasto = greedy_promocao(itens[:3], 250.0)

    resultado = {
        "brute_force": round(bf_valor, 2),
        "ga": ga,
        "greedy_promocional": round(gasto, 2),
    }

    saida = Path(__file__).resolve().parent / "resultados" / "resultado_q1.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Brute Force:", round(bf_valor, 2))
    print("GA:", ga)
    print("Greedy promocional:", round(gasto, 2))
    print("Arquivo salvo em:", saida)


if __name__ == "__main__":
    main()
