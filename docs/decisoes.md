# Decisoes de projeto

## Questao 1: fluxo implementado

1. A mesma funcao de avaliacao aplica elasticidade, estoque, taxas e margem minima
   ao Brute Force e ao Algoritmo Genetico.
2. O Brute Force enumera todas as combinacoes do subconjunto de benchmark.
3. O GA e executado no mesmo subconjunto para medir o gap e no catalogo completo
   disponivel para gerar a politica de precos.
4. O Greedy recebe essa politica e prioriza campanhas pelo beneficio incremental
   estimado por real, sem ultrapassar o orcamento.
5. A implementacao do GA usa um gerador aleatorio local, seed configuravel,
   elitismo e historico de fitness por geracao.

O catalogo presente em `questao_01/main.py` e apenas ilustrativo: o notebook e os
arquivos oficiais de entrada ainda precisam ser recuperados. O uplift promocional
de 10% e o custo por unidade baseado no custo logistico sao hipoteses explicitas
do prototipo, nao dados oficiais.

## Questao 2

A implementacao atual ainda e um prototipo. A integracao Monte Carlo -> DP ->
Greedy -> validacao independente esta pendente; consultar o PDF da avaliacao
antes de interpretar os resultados existentes.
