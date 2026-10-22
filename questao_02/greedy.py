from __future__ import annotations


def greedy_q2(itens, orcamento_promocional):
    """Alocação semanal simples de destaque promocional."""
    ordem = sorted(itens, key=lambda item: item["demanda_base_semanal"] * item["elasticidade"], reverse=True)
    gasto = 0.0
    for item in ordem:
        if gasto >= orcamento_promocional:
            break
        gasto += min(item["custo_logistico_base"], orcamento_promocional - gasto)
    return gasto
