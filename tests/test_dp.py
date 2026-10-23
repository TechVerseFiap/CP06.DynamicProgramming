from __future__ import annotations

from questao_01.brute_force import brute_force_q1
from questao_02.dynamic_programming import dynamic_programming_q2


def test_q1_small_case():
    itens = [
        {
            "sku": "A",
            "preco_atual": 100.0,
            "estoque": 30,
            "demanda_base_90d": 40,
            "elasticidade": 1.0,
            "taxa_marketplace": 0.10,
            "custo_unitario": 50.0,
            "custo_logistico": 8.0,
        }
    ]
    valor, _ = brute_force_q1(itens, [0.8, 0.9, 1.0], 0.05)
    assert valor >= 0


def test_q2_small_case():
    valor, _ = dynamic_programming_q2(
        demanda_base=10.0,
        elasticidade=1.0,
        estoque_inicial=5,
        preco_base=50.0,
        precos_permitidos=[0.8, 1.0],
        custo_unitario=25.0,
        custo_logistico=3.0,
        taxa_marketplace=0.10,
        semanas=2,
    )
    assert valor >= 0
