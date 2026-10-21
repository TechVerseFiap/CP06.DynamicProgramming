from __future__ import annotations

from itertools import product


def brute_force_q1(itens, price_levels, margem_minima):
    """Resolve exatamente um subconjunto pequeno por força bruta."""
    melhor = 0.0
    melhor_decisao = []

    for escolha in product(price_levels, repeat=len(itens)):
        caixa_total = 0.0
        decisao = []

        for item, mult in zip(itens, escolha):
            preco = item["preco_atual"] * mult
            demanda = min(item["estoque"], max(0, int(item["demanda_base_90d"] * (mult ** (-item["elasticidade"])))) )
            margem = preco * (1 - item["taxa_marketplace"]) - item["custo_unitario"] - item["custo_logistico"]
            if demanda <= 0 or margem <= 0 or margem < item["preco_atual"] * margem_minima:
                caixa = 0.0
            else:
                caixa = demanda * margem
            caixa_total += caixa
            decisao.append((item["sku"], preco, demanda))

        if caixa_total > melhor:
            melhor = caixa_total
            melhor_decisao = decisao

    return melhor, melhor_decisao
