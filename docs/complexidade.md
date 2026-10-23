# Complexidade

## Questao 1 (implementacao atual)

Definicoes: `N` = quantidade de SKUs, `P` = quantidade de multiplicadores de
preco permitidos, `G` = geracoes do GA e `K` = tamanho da populacao.

| Algoritmo | Tempo | Memoria auxiliar | Trecho dominante |
|---|---:|---:|---|
| Brute Force | O(N * P^N) | O(P + N) | Enumeracao de todas as politicas e avaliacao SKU a SKU. |
| Genetico | O(G * K * N) | O(K * N + G) | Avaliacao da populacao; crossover e mutacao tambem percorrem os genes. |
| Greedy | O(N log N) | O(N) | Ordenacao dos candidatos por beneficio incremental por real. |

O Brute Force deixa de ser pratico quando `P^N` cresce; ele e usado somente no
subconjunto reduzido. O GA e a alternativa heuristica para catalogos maiores.
O Greedy escala por SKU, mas sua qualidade depende das hipoteses de uplift e
custo promocional. Essas hipoteses ainda precisam ser substituidas pelos dados
oficiais do grupo.

## Questao 2 (prototipo; analise preliminar)

- Monte Carlo: O(C * F), onde `C` e o numero de cenarios e `F` o numero de
  fatores simulados; memoria O(C) na implementacao atual porque guarda todos os
  resultados.
- Programacao Dinamica: O(W * S * P), onde `W` e semanas, `S` e estoque maximo,
  e `P` e precos permitidos; memoria O(W * S).
- Greedy: O(N log N) no numero `N` de itens, devido a ordenacao.

As formulas e evidencias de desempenho da Questao 2 ainda precisam ser revistas
apos a integracao e medicao da validacao Monte Carlo exigida pela avaliacao.
