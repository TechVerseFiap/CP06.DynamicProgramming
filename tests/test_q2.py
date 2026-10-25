from __future__ import annotations

import unittest

from questao_02.dynamic_programming import dynamic_programming_catalog_q2
from questao_02.greedy import greedy_q2
from questao_02.main import run_q2
from questao_02.monte_carlo import monte_carlo_q2, validate_q2_policy


class QuestionTwoTests(unittest.TestCase):
    def setUp(self):
        self.items = [{
            "sku": "T1",
            "preco_atual": 100.0,
            "estoque_inicial": 40,
            "demanda_base_semanal": 8,
            "elasticidade": 1.0,
            "taxa_marketplace": 0.1,
            "custo_unitario": 40.0,
            "custo_logistico_base": 5.0,
        }]
        self.prices = [0.9, 1.0, 1.1]

    def test_monte_carlo_estimates_are_seed_reproducible(self):
        first = monte_carlo_q2(self.items, self.prices, scenarios=20, seed=4, weeks=3)
        second = monte_carlo_q2(self.items, self.prices, scenarios=20, seed=4, weeks=3)
        self.assertEqual(first, second)
        self.assertIn(("T1", 1, 1.0), first)
        self.assertGreater(first[("T1", 1, 1.0)]["expected_demand"], 0)

    def test_dp_reconstructs_weekly_stock_trajectory(self):
        estimates = monte_carlo_q2(self.items, self.prices, scenarios=20, seed=2, weeks=4)
        cash, policy = dynamic_programming_catalog_q2(self.items, estimates, self.prices, weeks=4)
        self.assertGreater(cash, 0)
        self.assertEqual([row["week"] for row in policy], [1, 2, 3, 4])
        stocks = [row["items"][0]["stock_end"] for row in policy]
        self.assertEqual(stocks, sorted(stocks, reverse=True))

    def test_greedy_weekly_budget_and_validation_milestones(self):
        estimates = monte_carlo_q2(self.items, self.prices, scenarios=20, seed=2, weeks=4)
        _, policy = dynamic_programming_catalog_q2(self.items, estimates, self.prices, weeks=4)
        promos = greedy_q2(self.items, policy, budget_per_week=20.0)
        self.assertEqual(len(promos), 4)
        self.assertTrue(all(row["spent"] <= 20.0 for row in promos))
        validation = validate_q2_policy(
            self.items, policy, promos, {2: 100.0, 4: 200.0}, scenarios=25, seed=5002
        )
        self.assertEqual(set(validation["payment_probability"]), {"2", "4"})
        self.assertGreaterEqual(validation["payment_probability"]["2"], 0)
        self.assertLessEqual(validation["payment_probability"]["2"], 1)

    def test_end_to_end_flow_uses_independent_validation_seed(self):
        result = run_q2(
            self.items, self.prices, seed=12, estimate_scenarios=20,
            validation_scenarios=30, promotion_budget=20,
            debt_schedule={2: 100.0, 4: 200.0}, weeks=4,
        )
        self.assertEqual(result["construction_scenarios"], 20)
        self.assertEqual(result["validation"]["validation_seed"], 1_000_015)
        self.assertEqual(len(result["weekly_policy"]), 4)

    def test_monte_carlo_rejects_nonpositive_scenario_count(self):
        with self.assertRaises(ValueError):
            monte_carlo_q2(self.items, self.prices, scenarios=0, weeks=1)


if __name__ == "__main__":
    unittest.main()
