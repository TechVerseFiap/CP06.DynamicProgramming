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

## Questao 2 (prototipo)

Definicoes: `N` = SKUs, `W` = semanas, `S` = estoque maximo por SKU, `P` =
multiplicadores de preco, `C` = cenarios Monte Carlo.

| Algoritmo | Tempo | Memoria auxiliar | Trecho dominante |
|---|---:|---:|---|
| Monte Carlo estimacao | O(N * W * P * C) | O(N * W * P) | Simulacao por SKU, semana, preco e cenario. |
| DP por SKU | O(N * W * S * P) | O(W * S + N * W) | Avaliacao de cada decisao em cada estado semana/estoque. |
| Greedy semanal | O(W * N log N) | O(W * N) | Ordenacao dos candidatos dentro de cada semana. |
| MC validacao | O(C * W * N) | O(C + W * N) | Simulacao independente da politica completa; armazena caixa final por cenario. |

As estimativas ainda sao independentes por preco e o objetivo da DP maximiza
caixa esperado, nao a probabilidade de quitar a divida. As medidas reais de
tempo/memoria, comparacoes entre tamanhos e limites de viabilidade continuam
pendentes.
