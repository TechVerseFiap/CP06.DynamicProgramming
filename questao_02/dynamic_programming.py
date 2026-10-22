from __future__ import annotations


def dynamic_programming_q2(demanda_base=60.0, elasticidade=1.2, estoque_inicial=25, preco_base=95.0,
                          precos_permitidos=None, custo_unitario=50.0, custo_logistico=6.0,
                          taxa_marketplace=0.10, semanas=12):
    """DP mínima em (semana, estoque)."""
    if precos_permitidos is None:
        precos_permitidos = [0.82, 0.88, 0.94, 1.00, 1.06, 1.12]

    n = semanas + 1
    dp = [[0.0 for _ in range(estoque_inicial + 1)] for _ in range(n)]

    for semana in range(semanas - 1, -1, -1):
        for estoque in range(estoque_inicial + 1):
            melhor = 0.0
            for mult in precos_permitidos:
                preco = preco_base * mult
                demanda = min(estoque, max(0, int(demanda_base * (mult ** (-elasticidade)))))
                if demanda <= 0:
                    continue
                margem = preco * (1.0 - taxa_marketplace) - custo_unitario - custo_logistico
                if margem <= 0:
                    continue
                caixa = demanda * margem
                estoque_restante = max(0, estoque - demanda)
                melhor = max(melhor, caixa + dp[semana + 1][estoque_restante])
            dp[semana][estoque] = melhor

    return dp[0][estoque_inicial], dp
