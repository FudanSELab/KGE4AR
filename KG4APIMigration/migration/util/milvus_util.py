import numpy as np
from milvus import Milvus, MetricType
from sklearn import preprocessing


class MilvusUtil:
    def __init__(self, milvus_connection: Milvus):
        self.milvus = milvus_connection

    def normalizer(self, vector_list, type='l2'):
        result = []
        try:
            vector_list = preprocessing.normalize(vector_list, type)
            for vector in vector_list:
                result.append(list(vector))
            return result
        except BaseException as e:
            print("MilvusUtil  normalize", e, vector_list)
            return []

    def query_vectors_by_ids(self, ids, collection_name, partition_name=None):
        return self.milvus.get_entity_by_id(collection_name=collection_name, ids=ids, partition_tag=partition_name)[1]

    def calculate_distance(self, vector_1, vector_2, type='ip'):
        try:
            if type == 'l2':
                print("ss")
                return np.sqrt(np.sum(np.square(np.array(vector_1) - np.array(vector_2))))
            return np.dot(vector_1, vector_2)
        except BaseException as e:
            print(e)
            return 0

    def batch_calculate_distance(self, vector_1, vectors_2):
        return list(np.dot(vector_1, vectors_2))

    def calculate_distance_by_id(self, id_1, id_2, collection_name, partition_name=None, type='ip'):
        ids = [id_1, id_2]
        vectors = self.query_vectors_by_ids(ids, collection_name, partition_name)

        return self.calculate_distance(vectors[0], vectors[1], type)

    def query_similar_vectors_ids_distances_by_ids(self, ids, collection_name, partion_name=None, top_k=10, type='ip', remove_self=True):
        entity_by_id = self.milvus.get_entity_by_id(collection_name=collection_name, ids=ids)
        records = entity_by_id[1]
        return self.query_similar_vectors_ids_dis_by_vertors(records, collection_name, partion_name, top_k, type, remove_self)

    def query_similar_vectors_ids_dis_by_vertors(self, records, collection_name, partion_name=None, top_k=10,
                                                 type='ip', remove_self=True):
        param = {
            "metric_type": MetricType.IP
        }
        if type == 'l2':
            param = {
                "metric_type": MetricType.L2
            }
        if remove_self == True:
            top_k = top_k + 1
        if partion_name is not None:
            partion_name = [partion_name]
        result_list_list = self.milvus.search(collection_name=collection_name, partition_tags=partion_name, query_records=records, top_k=top_k, params=param)[1]

        res = []
        dis = []
        for result_list in result_list_list:

            first = remove_self
            for result in result_list:
                if first:
                    first = False
                    continue
                res.append(result.id)
                dis.append(result.distance)

        return res, dis

    def average(self, vector_list) -> list:
        if len(vector_list) == 1:
            return vector_list[0]
        return list(np.average(vector_list, 0))
