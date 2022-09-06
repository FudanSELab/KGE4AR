# !/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd

def split2multicsv(file, chunksize):
    data = pd.read_csv(file, header=None, chunksize=chunksize, dtype=object)
    i = 0
    flies = file.split(".")
    for chunk in data:
        i += 1
        print(i)
        file = flies[0] + "_" + str(i) + ".tsv"
        chunk.to_csv(file, header=None, index=False)



if __name__ == '__main__':
    file = 'entity_embeddings_apikg_817_finetune829_9.tsv'
    chunk_size = 1000000
    split2multicsv(file, chunk_size)
