#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from pathlib import Path

from definitions import DATA_DIR, OUTPUT_DIR


class PathUtil:
    """
    provide a way to get a path of some common objects
    """

    @classmethod
    def combine_sim_collection(cls, name="word2vector_test"):
        """
        :param cache_name:
        :return:
        """
        return str(Path(OUTPUT_DIR) / "{cache_name}.simcol".format(cache_name=name))

    @classmethod
    def multi_combine_sim_collection(cls, name="word2vector_test"):
        """
        :param cache_name:
        :return:
        """
        return str(Path(OUTPUT_DIR) / "model" / "{cache_name}.msimcol".format(cache_name=name))

    @classmethod
    def temp_multi_combine_sim_collection(cls, name="word2vector_test"):
        """
        :param cache_name:
        :return:
        """
        return str(Path(OUTPUT_DIR) / "model" / "temp_model" / "{cache_name}.msimcol".format(cache_name=name))

    @classmethod
    def complex_relation_file(cls, name="relation_types_parameters_apikg_test_821.tsv"):
        """
        :param cache_name:
        :return:
        """
        return str(Path(DATA_DIR) / "query_data"/"{name}".format(name=name))


    @classmethod
    def evaluate_result(cls, name="word2vector_test"):
        """
        :param cache_name:
        :return:
        """
        return str(Path(OUTPUT_DIR) / "evaluate" / "{cache_name}.json".format(cache_name=name))