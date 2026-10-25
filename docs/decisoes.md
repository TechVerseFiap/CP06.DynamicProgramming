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

O catalogo Q1 e carregado dos arquivos oficiais gerados pelo notebook e so e
aceito depois da validacao SHA-256. O uplift promocional de 10% e o custo por
unidade baseado no custo logistico sao hipoteses do modelo, nao parametros
fornecidos pelo gerador; devem ser justificados na defesa.

## Questao 2: fluxo implementado no prototipo

1. Monte Carlo estima demanda e margem semanal por SKU e multiplicador, com
   variacoes de demanda, preco do concorrente e custo logistico.
2. A DP consome essas estimativas e reconstrui uma politica semanal por SKU,
   usando semana e estoque restante como estado.
3. O Greedy recebe a trajetoria da DP e escolhe incentivos semanais por caixa
   incremental estimado por real, respeitando o orcamento da semana.
4. A politica final e reavaliada com um RNG e seed separados, em pelo menos
   5.000 cenarios por padrao. A validacao reporta probabilidade de pagamento
   nos marcos da divida, caixa esperado, P10, estoque final e exemplos de falha.

O catalogo e os valores de divida/caixa agora vem dos arquivos oficiais gerados
para G01, validados por SHA-256. As variabilidades usadas pelo Monte Carlo tambem
vem do config oficial. O uplift promocional de 10% e o custo por unidade baseado
no custo logistico seguem sendo hipoteses do modelo. A DP maximiza caixa esperado,
nao diretamente a probabilidade de pagamento; esse limite deve ser explicitado.
