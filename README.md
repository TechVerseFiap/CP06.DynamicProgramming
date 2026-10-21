# Checkpoint 6 — Dynamic Programming

## Grupo
Grupo: G01

Integrantes:
- Davi Marques de Andrade Munhoz — RM 566223
- Diogo Oliveira Lima — RM 562559
- Leandro Simoneli da Silva — RM 566539
- Lucas dos Reis Aquino — RM 562414
- Lucas Perez Bonato — RM 565356

## Seed base
Seed base: 0

## Seed final
Seed final: 1001

## ID da instância
ID da instância: G01_2026_01

## Estrutura do repositório

```text
avaliacao-varejo-grupo01/
├── README.md
├── requirements.txt
├── IA_USO.md
├── data/
│   ├── instancia_grupo01.csv
│   └── manifesto_dados.json
├── questao_01/
│   ├── brute_force.py
│   ├── genetic_algorithm.py
│   ├── greedy.py
│   ├── main.py
│   └── resultados/
├── questao_02/
│   ├── monte_carlo.py
│   ├── dynamic_programming.py
│   ├── greedy.py
│   ├── main.py
│   └── resultados/
├── tests/
├── docs/
│   ├── arquitetura.png
│   ├── complexidade.md
│   ├── desempenho.md
│   └── decisoes.md
└── .gitignore
```

## Objetivo
Este repositório implementa a solução de duas questões de Dynamic Programming para a avaliação de precificação online de varejo, com foco em:
- maximização de caixa;
- controle de margem;
- gestão de estoques;
- planejamento semanal sob incerteza.

## Execução rápida
```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python questao_01/main.py --modo completo
python questao_02/main.py --seed 14 --cenarios 5000
```

## Observação
As duas soluções usam modelagem de programação dinâmica, com validação por exemplos e casos limites. O código foi organizado para manter o fluxo de algoritmos em cada questão e permitir reprodução dos resultados.
