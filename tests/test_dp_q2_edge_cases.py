from __future__ import annotations

import unittest

from questao_02.dynamic_programming import dynamic_programming_q2


class DynamicProgrammingQ2EdgeCases(unittest.TestCase):
    def test_hand_calculated_single_week(self):
        # Demand 10, stock 5 -> sells 5 units.
        # Margin = 50 * (1 - 0.10) - 25 - 3 = 17 -> cash = 5 * 17 = 85
        valor, _ = dynamic_programming_q2(
            demanda_base=10.0,
            elasticidade=1.0,
            estoque_inicial=5,
            preco_base=50.0,
            precos_permitidos=[1.0],
            custo_unitario=25.0,
            custo_logistico=3.0,
            taxa_marketplace=0.10,
            semanas=1,
        )
        self.assertAlmostEqual(valor, 85.0)

    def test_zero_stock_returns_zero(self):
        valor, _ = dynamic_programming_q2(estoque_inicial=0)
        self.assertEqual(valor, 0.0)

    def test_negative_margin_returns_zero(self):
        # Price below unit cost: no sale should be worth making.
        valor, _ = dynamic_programming_q2(preco_base=40.0, custo_unitario=50.0)
        self.assertEqual(valor, 0.0)


if __name__ == "__main__":
    unittest.main()
