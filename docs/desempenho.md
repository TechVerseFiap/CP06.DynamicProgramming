# Desempenho e medições

Medições executadas no Windows com Python 3.14.4, NumPy 2.4.6 e pandas 3.0.3,
na instância `ec52f3b45b22`, seed de construção Q2 1232. A ferramenta envolve as
chamadas com `time.perf_counter()` e `tracemalloc`; portanto os tempos incluem a
sobrecarga de rastreamento de alocações e servem principalmente para comparar
as mesmas rotinas neste ambiente. Os CSVs completos, inclusive memória de pico,
estão em `questao_01/resultados/performance.csv`,
`questao_01/resultados/ga_config_performance.csv` e
`questao_02/resultados/performance.csv`.

## Questão 1

| Algoritmo/configuração | SKUs | Tempo (s) | Pico (MiB) |
|---|---:|---:|---:|
| Brute Force referência | 6 | 2.985312 | 0.0040 |
| Brute Force otimizado | 6 | 0.559513 | 0.0194 |
| GA baseline (K=30, G=50, mutação=0.1) | 30 | 0.399735 | 0.0304 |
| GA exploração (K=60, G=100, mutação=0.2) | 30 | 1.730952 | 0.0562 |
| Greedy | 30 | 0.000177 | 0.0053 |

O Brute Force otimizado pré-calcula resultado por SKU/preço; o benchmark de seis
SKUs produziu o mesmo caixa (`57345.99`) e foi aproximadamente 5.3x mais rápido
que a versão de referência neste ambiente. A configuração exploratória do GA
gastou mais tempo/memória e obteve caixa um pouco menor neste seed; a curva de
fitness está em `questao_01/resultados/ga_fitness_convergence.svg`.
Os tamanhos pequenos/médios/grandes e os resultados por configuração podem ser
consultados no CSV de performance e na tabela `ga_config_performance.csv`.

## Questão 2

| Algoritmo | SKUs | Cenários | Tempo (s) | Pico (MiB) |
|---|---:|---:|---:|---:|
| Monte Carlo estimativa | 3 | 2.000 | 7.406001 | 0.5658 |
| Risk-aware DP | 3 | — | 45.551182 | 1.9369 |
| Greedy semanal | 3 | — | 0.000167 | 0.0028 |
| Monte Carlo validação | 3 | 5.000 | 1.525710 | 0.3441 |
| Monte Carlo estimativa | 12 | 2.000 | 27.894347 | 1.3576 |
| Risk-aware DP | 12 | — | 105.655469 | 3.7700 |
| Greedy semanal | 12 | — | 0.000248 | 0.0012 |
| Monte Carlo validação | 12 | 5.000 | 11.064260 | 0.7009 |
| Monte Carlo estimativa | 24 | 2.000 | 56.008272 | 2.5441 |
| Risk-aware DP | 24 | — | 184.524725 | 6.6870 |
| Greedy semanal | 24 | — | 0.000933 | 0.0066 |
| Monte Carlo validação | 24 | 5.000 | 27.663527 | 1.4262 |

A DP usa 10 buckets de caixa e 5 transições quantílicas por ação. O tempo cresce
com SKUs, semanas, estoque máximo e buckets; se isso ficar inviável, reduzir
resolução dos buckets ou usar uma política aproximada e validar o risco por
Monte Carlo. Os CSVs registram semanas, preços, cenários e seeds usados.

## Reproduzir

```bash
python tools/benchmark_performance.py
python tools/evidence.py
```

Esses comandos usam os dados oficiais validados por SHA-256 e recriam os CSVs,
curvas e gráficos. As comparações são específicas desta instância/máquina e não
devem ser apresentadas como garantia de desempenho em outro ambiente.
