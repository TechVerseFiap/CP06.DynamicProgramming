from __future__ import annotations

import unittest

from questao_01.brute_force import brute_force_q1
from questao_01.genetic_algorithm import genetic_algorithm_q1
from questao_01.greedy import greedy_promocao
from questao_01.metrics import apply_promotions, evaluate_policy
from questao_01.main import carregar_catalogo, run_q1


class QuestionOneTests(unittest.TestCase):
    def setUp(self):
        self.items = carregar_catalogo()
        self.prices = [0.8, 1.0, 1.1]

    def test_policy_respects_stock_and_margin_floor(self):
        cash, policy = evaluate_policy(self.items[:1], [1.0], 0.05)
        expected_demand = int(self.items[0]["demanda_base_90d"])
        expected_units = min(self.items[0]["estoque"], expected_demand)
        self.assertEqual(policy[0]["units"], expected_units)
        self.assertEqual(
            policy[0]["remaining_stock"], self.items[0]["estoque"] - expected_units
        )
        self.assertGreaterEqual(cash, 0)

    def test_brute_force_returns_exact_best_policy(self):
        cash, policy = brute_force_q1(self.items[:2], self.prices, 0.05)
        evaluated, _ = evaluate_policy(
            self.items[:2], [entry["multiplier"] for entry in policy], 0.05
        )
        self.assertAlmostEqual(cash, evaluated)
        self.assertEqual(len(policy), 2)

    def test_brute_force_precomputation_preserves_exact_optimum(self):
        from itertools import product

        expected = max(
            evaluate_policy(self.items[:3], multipliers, 0.05)[0]
            for multipliers in product(self.prices, repeat=3)
        )
        actual, _ = brute_force_q1(self.items[:3], self.prices, 0.05)
        self.assertAlmostEqual(expected, actual)

    def test_ga_is_seeded_and_returns_fitness_history(self):
        first = genetic_algorithm_q1(self.items[:3], self.prices, 0.05, seed=123)
        second = genetic_algorithm_q1(self.items[:3], self.prices, 0.05, seed=123)
        self.assertEqual(first, second)
        self.assertEqual(len(first["fitness_history"]), 51)
        self.assertEqual(len(first["policy"]), 3)

    def test_ga_rejects_invalid_parameters(self):
        with self.assertRaises(ValueError):
            genetic_algorithm_q1(self.items, [], 0.05)
        with self.assertRaises(ValueError):
            genetic_algorithm_q1(self.items, self.prices, 0.05, mutation_rate=1.1)

    def test_greedy_policy_allocation_obeys_budget(self):
        ga = genetic_algorithm_q1(self.items, self.prices, 0.05, seed=5)
        result = greedy_promocao(self.items, ga["policy"], 250.0)
        self.assertLessEqual(result["spent"], 250.0)
        self.assertAlmostEqual(result["spent"] + result["remaining_budget"], 250.0)
        self.assertTrue(all(row["incremental_cash"] >= 0 for row in result["allocations"]))

    def test_promotional_units_are_included_in_post_greedy_accounting(self):
        item = dict(self.items[0])
        item["estoque"] = 1000
        _, policy = evaluate_policy([item], [1.0], 0.0)
        promotions = {
            "spent": 2.0,
            "allocations": [{"sku": item["sku"], "extra_units": 3, "cost": 2.0}],
        }
        post = apply_promotions(policy, promotions)[0]
        self.assertEqual(post["units"], policy[0]["units"] + 3)
        self.assertEqual(post["remaining_stock"], policy[0]["remaining_stock"] - 3)
        self.assertAlmostEqual(
            post["cash"], policy[0]["cash"] + 3 * policy[0]["unit_margin"] - 2.0
        )

    def test_main_pipeline_connects_benchmark_ga_and_greedy(self):
        result = run_q1(self.items[:6], self.items, self.prices, 0.05, 14, 250.0)
        self.assertEqual(result["benchmark"]["sku_count"], 6)
        self.assertEqual(
            len(result["full_catalog_ga"]["policy_after_greedy"]), len(self.items)
        )
        self.assertLessEqual(result["greedy_promotion"]["spent"], 250.0)


if __name__ == "__main__":
    unittest.main()
