# kge4am.github.io
## Our project
The code of our project is divided into two parts, the knowledge graph construction code and the migration code.
1. [KG4APIMigration](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration), the migration code.
2. [KGBuilder](https://github.com/kge4am/kge4am.github.io/blob/main/KGBuilder), knowledge graph construction code.
    
## Our data
### Test data set
1. [APIMigrationBenchmark](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/data/query_data/APIMigrationBenchmark.csv), this is our final test migration data pair. We have 270 test migration data pairs in total.
2. [QueryDataRelateLibrary](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/data/query_data/QueryDataRelateLibrary.csv), this is all the libraries involved in our migration of the dataset.
### Knowledge graph
1. [libraries.io](https://zenodo.org/record/3626071/files/libraries-1.6.0-2020-01-12.tar.gz), the download address of the original data set we built the knowledge graph.
2. [BigKGData](todo), data directory of big knowledge graph.
3. [BigKGEmbedding](todo), embedding directory of big knowledge graph.
4. [BigKGRelatedLibrary](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/data/query_data/BigKGRelateLibrary.csv), all libraries involved in the big knowledge graph.
5. [MiddleKGData](todo), data directory of middle knowledge graph.
6. [SmallKGData](todo), data directory of small knowledge graph.
7. [SmallKGEmbedding](todo), embedding directory of small knowledge graph.


## Our result
### RQ1
1. [KGE4AM-Ret](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/big_apimigration_retrieve_filter.json), performance on KGE4AM-Ret with given target libraries.
2. [KGE4AM](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/big_apimigration_rerank_filter.json), performance on KGE4AM with given target libraries.
3. [KGE4AMScript](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/script/temp_data_op/generate_temp_data_for_method.py), the script of KGE4AM with given target libraries.
4. [RAPIM](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/big_rapim_filter.json), performance on RAPIM with given target libraries.
5. [RAPIMScript](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/script/rapim/generate_temp_data_for_rapim_method.py), the script of RAPIM with given target libraries.
6. [D2APIMap](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/big_d2apimap_filter.json), performance on D2APIMap with given target libraries.
7. [D2APIMapScript](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/script/d2apimap/generate_temp_data_for_d2apimap_method.py), the script of D2APIMap with given target libraries.
### RQ2
1. [KGE4AM](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/mark_result/big_sample_kge4am_method_10.json), sample data on KGE4AM without given target libraries.
2. [BM25](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/mark_result/big_sample_bm25_method_10.json), sample data on BM25 without given target libraries.
3. [BM25+RAPIM](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/mark_result/big_sample_rapim_method_10.json), sample data on BM25+RAPIM without given target libraries.
4. [BM25+D2APIMap](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/mark_result/big_sample_d2apimap_method_10.json), sample data on BM25+D2APIMap without given target libraries.
5. [FinalMarkResult](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/mark_result/big_final_mark.csv), mark result between KGE4AM and baselines without given target libraries. 
### RQ3
1. [DiffKGEmbeddingScript](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/script/temp_data_op/generate_single_parameter_temp_data_for_method.py), the script of different knowledge graph embedding models.
2. [DiffKGEmbeddingPerformance](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/different_kg_embedding), performance on different method knowledge graph embedding models.
3. [DiffKGEmbeddingVector](todo), vector on different method knowledge graph embedding models.
4. [DiffKnowledgePerformance](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/delete_one_rerank_parameter.json), the performance of different knowledge types. 
5. [DiffKnowledgeTypeScript](https://github.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/script/generate_single_parameter_temp_data_for_method.py), the script of different knowledge types. 
6. [ContributionOfDiffSimilarity](https://gsithub.com/kge4am/kge4am.github.io/blob/main/KG4APIMigration/output/evaluate/delete_one_rerank_parameter.json), the contribution of different similarity in the rerank step.