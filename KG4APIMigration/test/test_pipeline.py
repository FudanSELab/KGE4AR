from unittest import TestCase

from calculator.example import ConstantSimCalculator
from pipeline import APIMigration


class TestAPIMigration(TestCase):
    def test_batch_sim(self):
        migration = APIMigration()
        migration.add_calculator(calculator=ConstantSimCalculator())
        self.assertIsNotNone(migration.retrieval(1, 100))

    def test_pair_sim(self):
        migration = APIMigration()
        migration.add_calculator(calculator=ConstantSimCalculator())
        self.assertIsNotNone(migration.pair_sim(1, 2))
