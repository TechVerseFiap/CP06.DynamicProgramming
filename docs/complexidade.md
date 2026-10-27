# Complexidade

## Questao 1 (implementacao atual)

Definicoes: `N` = quantidade de SKUs, `P` = quantidade de multiplicadores de
preco permitidos, `G` = geracoes do GA e `K` = tamanho da populacao.

| Algoritmo | Tempo | Memoria auxiliar | Trecho dominante |
|---|---:|---:|---|
| Brute Force | O(N * P + N * P^N) | O(N * P + N) | Precalculo por SKU/preco, depois enumeracao cartesiana e soma dos resultados. |
| Genetico | O(G * K * N) | O(K * N + G) | Avaliacao da populacao; crossover/mutacao percorrem genes e fitness salva G pontos. |
| Greedy | O(N log N) | O(N) | Ordenacao dos candidatos por beneficio incremental por real. |

O Brute Force deixa de ser pratico quando `P^N` cresce; ele e usado somente no
subconjunto reduzido. O GA e a alternativa heuristica para catalogos maiores.
O Greedy escala por SKU, mas sua qualidade depende das hipoteses de uplift e
custo promocional. Essas hipoteses ainda precisam ser substituidas pelos dados
oficiais do grupo.

## Questao 2

Definicoes: `N` = SKUs, `W` = semanas, `S` = estoque maximo por SKU, `P` =
multiplicadores de preco, `C` = cenarios e `B` = cash buckets por SKU na DP.
`R=5` representa os resultados de quantil usados para aproximar a transicao
estocastica na DP.

| Algoritmo | Tempo | Memoria auxiliar | Trecho dominante |
|---|---:|---:|---|
| Monte Carlo estimacao | O(N * W * P * C log C) | O(C + N * W * P * R) | Simulacao e ordenacao de cenarios por SKU/semana/preco para obter quantis. |
| Risk-aware DP | O(N * W * S * B * P * R) | O(N * W * S * B + N * W) | Avaliacao de cada acao/quantil em estado semana/estoque/cash-bucket; guarda a tabela de politica. |
| Greedy semanal | O(W * N log N) | O(W * N) | Ordenacao dos candidatos dentro de cada semana. |
| MC validacao | O(C * W * N) | O(C * N + W * N) | Simulacao independente; guarda caixa final e estoque final por SKU/cenario. |

O Brute Force torna-se inviavel quando `P^N` cresce; por isso fica restrito ao
subconjunto de seis SKUs e o GA e usado no catalogo completo. A DP usa dez
cash-buckets e cinco quantis de transicao; e uma aproximacao limitada, cuja
probabilidade real de pagamento e medida pela validacao Monte Carlo independente.
O custo da DP cresce com o estoque maximo e com B; reduzir buckets economiza
tempo/memoria, mas perde resolucao de caixa. As medições do grupo estão em
`questao_01/resultados/performance.csv` e `questao_02/resultados/performance.csv`.
