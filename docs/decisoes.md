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

**Nesta questão utilizamos 3 algoritmos:** Brute Force encontra o ótimo exato
no subconjunto de seis SKUs; o Algoritmo Genético compara esse benchmark e
produz a política do catálogo completo; o Greedy usa essa política para aplicar
incentivos dentro do orçamento. A saída pós-Greedy recalcula caixa, margem e
estoque após as unidades incrementais e seus custos promocionais.

A comparação GA usa duas configurações com o mesmo seed: baseline (K=30, G=50,
mutação=0.1) e exploração (K=60, G=100, mutação=0.2). A seleção mantém um terço
da população como elites, escolhe pais entre as elites, faz crossover uniforme,
mutação por gene e para após o número fixo de gerações. A evidência de fitness e
as métricas comparativas são geradas em `questao_01/resultados/`.

O catalogo Q1 e carregado dos arquivos oficiais gerados pelo notebook e so e
aceito depois da validacao SHA-256. O uplift promocional de 10% e o custo por
unidade baseado no custo logistico sao hipoteses do modelo, nao parametros
fornecidos pelo gerador; devem ser justificados na defesa.

## Questao 2: fluxo risk-aware implementado

1. Monte Carlo estima demanda e margem semanal por SKU e multiplicador, com
   variacoes de demanda, preco do concorrente e custo logistico.
2. A DP consome essas estimativas e reconstrui uma politica semanal por SKU,
   usando semana e estoque restante como estado.
3. O Greedy recebe a trajetoria da DP e escolhe incentivos semanais por caixa
   incremental estimado por real, respeitando o orcamento da semana.
4. A politica final e reavaliada com um RNG e seed separados, em pelo menos
   5.000 cenarios por padrao. A validacao reporta probabilidade de pagamento
   nos marcos da divida, caixa esperado, P10, estoque final e exemplos de falha.

**Nesta questão utilizamos 3 algoritmos:** Monte Carlo estima os resultados
possíveis por SKU/preço; a Programação Dinâmica escolhe decisões considerando
semana, estoque restante e um bucket conservador de caixa; Greedy aloca o
orçamento promocional semanal ao plano. Dois planos DP (focado em caixa esperado
e risco-aware) são comparados em pelo menos 2.000 cenários de construção; escolhe-se
o de maior probabilidade de pagar todos os compromissos no prazo, com desempate
por P10 e caixa esperado. Um seed independente e pelo menos 5.000 cenários são
reservados à validação final.

O catalogo e os valores de divida/caixa agora vem dos arquivos oficiais gerados
para G01, validados por SHA-256. As variabilidades usadas pelo Monte Carlo tambem
vem do config oficial. O uplift promocional de 10% e o custo por unidade baseado
no custo logistico seguem sendo hipoteses do modelo. A DP usa aproximação de
quantis e buckets de caixa; por SKU maximiza a fração esperada de obrigações
alocadas pagas no prazo. A seleção Monte Carlo escolhe entre os planos DP pela
probabilidade conjunta de cumprir os três prazos. A validação final é independente
da seleção e fornece a estimativa reportada.
