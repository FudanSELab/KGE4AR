import json
from migration.calculator.base import MultiCombineSimResultCollection, CombineSimResultCollection
from migration.util.path_util import PathUtil
import numpy as np
from migration.evaluate.dataset import DataSet



class SimEvaluator:

    def __init__(self, top_n=100):
        self.eval_result = {}
        self.top_n = top_n

    def evaluate(self, dataset: DataSet,  top_n_list: [], multi_combine_sim_result_collection: MultiCombineSimResultCollection, combine_sim_result_collection_type: str, msimcol_name: str, multi_data: [] = [], name2weight: dict = {}, node_filter=None, filter_in_class=False, filter_in_library=False) -> dict:
        self.eval_result = {}
        id2name2sim_collection = multi_combine_sim_result_collection.id2name2sim_collection

        detail_data = {
            "query_num": 0,
            "name2weight": dict({}),
            "type": combine_sim_result_collection_type,
            "msimcol_name": msimcol_name
        }
        temp_mrr = []
        temp_rank = []
        temp_hit_num = []
        hit_position = [0 for i in range(self.top_n)]
        top_n_hit = {}
        for top_n in top_n_list:
            top_n_hit[str(top_n)] = 0
        if multi_data == []:
            for query_pair in dataset.query_data:
                temp_query_pair = [{"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
                                   {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}]
                for t in temp_query_pair:
                    # print("process", temp_query_pair)
                    csrc: CombineSimResultCollection = id2name2sim_collection.get(str(t.get("query_id")) + "_" + str(t.get("target_id")), None)
                    if csrc is not None:
                        detail_data["query_num"] = detail_data["query_num"] + 1

                        for name, weight in csrc.name2weight.items():
                            detail_data["name2weight"][name] = name2weight.get(name, weight)
                        sr_list = csrc.get_combine_sim_result(name2weight=name2weight)
                        prediction = [sr.end_id for sr in sr_list]
                        if node_filter is not None:
                            # if filter_in_class:
                            #     prediction = node_filter.filter_method_in_one_class(prediction)
                                if filter_in_library:
                                    prediction = node_filter.filter_method_in_one_library(prediction, 3)
                        mrr, rank, hit_num = self.__mrr_rank_hit_num_n(t.get("target_id"), prediction)
                        for top_n in top_n_list:
                            top_n_hit[str(top_n)] = top_n_hit[str(top_n)] + self.__hit_num_n(t.get("target_id"), prediction, top_n)
                        if int(rank) <= self.top_n:
                            hit_position[int(rank)-1] = hit_position[int(rank)-1] + 1
                        temp_mrr.append(mrr)
                        temp_rank.append(rank)
                        temp_hit_num.append(hit_num)
                    else:
                        print("none")
        else:
            temp_result = multi_combine_sim_result_collection.multi_get_combine_sim_result(multi_data[0], multi_data[1], multi_data[2], name2weight)

            for name, weight in multi_data[3].items():
                detail_data["name2weight"][name] = name2weight.get(name, weight)

            for query_pair in dataset.query_data:
                temp_query_pair = [{"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
                                   {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}]
                for t in temp_query_pair:
                    prediction = temp_result.get(str(t.get("query_id")) + "_" + str(t.get("target_id")), None)
                    if prediction is not None:
                        if node_filter is not None:
                            # if filter_in_class:
                            #     prediction = node_filter.filter_method_in_one_class(prediction)
                                if filter_in_library:
                                    prediction = node_filter.filter_method_in_one_library(prediction, 3)
                        detail_data["query_num"] = detail_data["query_num"] + 1

                        mrr, rank, hit_num = self.__mrr_rank_hit_num_n(t.get("target_id"), prediction)
                        for top_n in top_n_list:
                            top_n_hit[str(top_n)] = top_n_hit[str(top_n)] + self.__hit_num_n(t.get("target_id"), prediction,
                                                                                             top_n)
                        if int(rank) <= self.top_n:
                            hit_position[int(rank) - 1] = hit_position[int(rank) - 1] + 1
                        temp_mrr.append(mrr)
                        temp_rank.append(rank)
                        temp_hit_num.append(hit_num)
                    else:
                        print("none")
        all_hit_num = 0.0 + np.sum(temp_hit_num)
        avg_rank = np.mean(temp_rank)
        avg_mrr = np.mean(temp_mrr)
        avg_hit = np.mean(temp_hit_num)
        rank_count = {}
        for index, i in enumerate(hit_position):
            if i != 0:
                rank_count["rank_" + str(index+1)] = i

        if int(all_hit_num) == 0:
            avg_mrr_filter = 0
        else:
            avg_mrr_filter = float(np.sum(temp_mrr))/all_hit_num
        avg_rank_filter = 0
        for index, i in enumerate(hit_position):
            avg_rank_filter = avg_rank_filter + (index+1)*i
        if int(all_hit_num) == 0:
            avg_rank_filter = self.top_n + 1
        else:
            avg_rank_filter = avg_rank_filter/all_hit_num
        for k, v in top_n_hit.items():
            top_n_hit[k] = v / detail_data["query_num"]

        self.eval_result = {"mrr": avg_mrr, "mrr_filter": avg_mrr_filter, "rank": avg_rank, "rank_filter": avg_rank_filter, "hit": avg_hit, "hit_num": all_hit_num, "rank_count": rank_count, "top_n_hit": top_n_hit,  "top_n": self.top_n, "details": [detail_data]}
        return self.eval_result

    def evaluate_for_single_api(self, dataset: DataSet,
                                combine_sim_result_collection: CombineSimResultCollection) -> dict:
        return {"mrr": 0, "details": []}

    def __mrr_rank_hit_num_n(self, ground_truth, prediction):
        prediction = prediction[:self.top_n]
        for idx, pred in enumerate(prediction):
            if pred == ground_truth:
                return 1.0 / (1.0 + idx), 1.0 + idx, 1
        return 0.0, 1.0 + self.top_n, 0

    def __mrr_n(self, ground_truth, prediction):
        prediction = prediction[:self.top_n]
        for idx, pred in enumerate(prediction):
            if pred == ground_truth:
                return 1.0 / (1.0 + idx)
        return 0.0

    def __rank_n(self, ground_truth, prediction):
        prediction = prediction[:self.top_n]
        for idx, pred in enumerate(prediction):
            if pred == ground_truth:
                return 1.0 + idx
        return 1.0 + self.top_n

    def __hit_num_n(self, ground_truth, prediction, top_n):
        prediction = prediction[:top_n]
        for idx, pred in enumerate(prediction):
            if pred == ground_truth:
                return 1
        return 0

    def save_2_json_file(self, data, file_name):
        with open(PathUtil.evaluate_result(file_name), 'w') as f:
            json.dump(data, f)

if __name__ == '__main__':
    pass