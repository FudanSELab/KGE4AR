# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/11
------------------------------------------
@Modify: 2022/08/11
------------------------------------------
@Description:
"""
from migration.d2apimap.model import Word2VectorModel
from migration.d2apimap.sentence_pipeline import SentencePipeline

type = "big"

file2property = {
    "method": "method_with_description_{}.csv".format(type),
    "return_value": "return_value_with_description_{}.jl".format(type),
    "parameter": "parameter_with_description_{}.jl".format(type),
}


pipe = SentencePipeline(name_keyword_list_file="name_keyword_list_{}.txt".format(type))
word2vector = Word2VectorModel(pipe)
# word2vector.gene_model(file2property, "word2vector_{}".format(type), min_count=1, window=5, vector_size=256)
word2vector.load_model("word2vector_{}".format(type))

print(word2vector.model.wv["title"])
print(len(word2vector.model.wv.key_to_index))

# 生成name_keyword_list
# sp = SentencePipeline(name_keyword_list_file="name_keyword_list_{}.txt".format(type))
# model = Word2VectorModel(sp)
# model.gene_name_token_list(file2property["method"], "name_keyword_list_{}.txt".format(type))

