# Checkpoint 6 - Dynamic Programming

## Group and instance

- Group: G01
- Members: Davi Marques de Andrade Munhoz (RM 566223), Diogo Oliveira Lima
  (RM 562559), Leandro Simoneli da Silva (RM 566539), Lucas dos Reis Aquino
  (RM 562414), and Lucas Perez Bonato (RM 565356)
- Seed base: 0
- Seed final: 1001
- Instance ID: G01_2026_01

> **Data status:** the repository currently uses illustrative sample catalogs.
> They are not the official group-generated inputs. Do not submit their numeric
> results as official until the generator notebook and official CSV/config files
> are restored and wired into the programs.

## Environment

Python 3.10 or newer is recommended. Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Question 1 sample run

```bash
python questao_01/main.py --seed 14 --orcamento-promocional 250
```

The command runs the six-SKU Brute Force benchmark, the seeded GA on that
benchmark and the available catalog, then passes the GA price policy to Greedy.
It writes `questao_01/resultados/resultado_q1.json`, including the policies,
benchmark gap, GA fitness history, and promotion allocations. The sample uses an
illustrative 10% demand uplift and logistics cost as the per-unit incentive cost.

## Tests

```bash
python -m unittest discover -s tests -p "test_q1.py" -v
```

The existing Question 2 implementation remains a prototype; its sample command
is `python questao_02/main.py --seed 14 --cenarios 5000`. See `docs/decisoes.md`
and `docs/complexidade.md` for current limitations and complexity assumptions.

## Official instance status

The current `data/manifesto_dados.json` does not yet contain the official input
hashes. Recover the generator and generated files, then verify and record hashes
before using numeric results as official submission evidence.
