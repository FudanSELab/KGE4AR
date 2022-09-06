#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
from migration.calculator.base import SimCalculator, SimResult


class ConstantSimCalculator(SimCalculator):
    def __init__(self, ):
        super().__init__()

    def batch_sim(self, start_api_id, top_n=500) -> List[SimResult]:
        result = [SimResult(start_id=start_api_id, end_id=i, score=0.7) for i in range(0, top_n)]
        return result

    def pair_sim(self, start_api_id, end_api_id):
        return SimResult(start_api_id, end_api_id, 0.7)
