from __future__ import annotations


def greedy_promocao(itens, orcamento_promocional):
    """Distribui incentivo de acordo com maior benefício marginal por real investido."""
    itens_ordenados = []
    for item in itens:
        ganho = min(item["estoque"], max(0, int(item["demanda_base_90d"] * (1.0 / (1.0 + item["elasticidade"])) )) ) * (
            item["preco_atual"] * (1 - item["taxa_marketplace"]) - item["custo_unitario"] - item["custo_logistico"]
        )
        beneficio = ganho / max(1.0, item["custo_logistico"])
        itens_ordenados.append((beneficio, item))

    itens_ordenados.sort(reverse=True)
    gasto = 0.0
    for _, item in itens_ordenados:
        if gasto >= orcamento_promocional:
            break
        gasto += min(item["custo_logistico"], orcamento_promocional - gasto)

    return gasto
