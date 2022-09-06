# !/usr/bin/env python
# -*- coding: utf-8 -*-
from migration.rapim.model import TfIdfModel
from migration.rapim.sentence_pipeline import SentencePipeline


type = "big"


file2property = {
    "method": "method_with_description_{}.csv".format(type),
    "return_value": "return_value_with_description_{}.jl".format(type),
    "parameter": "parameter_with_description_{}.jl".format(type),
}

pipe = SentencePipeline()
tfidf = TfIdfModel(pipe)
tfidf.gene_model_and_dictionary(file2property, "tfidf_{}".format(type), "token2id_{}.txt".format(type))
