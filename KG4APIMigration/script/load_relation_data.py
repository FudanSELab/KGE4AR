import numpy as np
import torch

from definitions import RemoteMilvus
from migration.util.path_util import PathUtil
# 参考官网教程书写：https://github.com/facebookresearch/PyTorch-BigGraph/blob/26e23ee1fe4c66c14e66ac09f2e6cf5c71c8452a/docs/source/downstream_tasks.rst
from migration.util.db_util import DBUtil


def ComplexDiagonalDynamicOperator(embeddings, real_b, imag_b, dim):
    real_a = embeddings[..., : dim // 2]
    imag_a = embeddings[..., dim // 2:]
    prod = torch.empty_like(embeddings)
    prod[..., : dim // 2] = real_a * real_b - imag_a * imag_b
    prod[..., dim // 2:] = real_a * imag_b + imag_a * real_b
    return prod


def DotComparator(embedding1, embedding2):
    result = (embedding1 * embedding2).sum(-1)
    return result


if __name__ == "__main__":

    r_file = PathUtil.complex_relation_file()

    embeddings = np.loadtxt(
        r_file,
        dtype=np.float32,
        delimiter="\t",
        skiprows=0,
        max_rows=78404883,
        usecols=range(5, 5 + 128),
        comments=None,
    )

    relation2numpy_map = {}

    lines = []
    for line in open(r_file):
        line = line.strip()
        if len(line) == 0:
            continue
        # print(line)
        lines.append(line)

    for index, line in enumerate(lines):
        cols = line.split("\t")
        # print(cols)
        relation_name = cols[0]
        r_type = cols[1]
        part = cols[3]
        if relation_name not in relation2numpy_map:
            relation2numpy_map[relation_name] = {}
        if r_type not in relation2numpy_map[relation_name]:
            relation2numpy_map[relation_name][r_type] = {}
        if part not in relation2numpy_map[relation_name][r_type]:
            relation2numpy_map[relation_name][r_type][part] = {}

        relation2numpy_map[relation_name][r_type][part] = embeddings[index]
    # print(relation2numpy_map)
    # print(embeddings)
    dynamic_rel_count = len(relation2numpy_map)

    head_entity_id = 4
    relation_type = "extends"
    tail_entity_id = 174

    # get relation embedding
    relation_real = torch.from_numpy(relation2numpy_map[relation_type]["rhs"]["real"])
    relation_imag = torch.from_numpy(relation2numpy_map[relation_type]["rhs"]["imag"])

    # get entity embedding
    MU = DBUtil.get_milvus_util()
    embedding1 = torch.tensor(
        MU.query_vectors_by_ids(ids=[head_entity_id], collection_name=RemoteMilvus.TEST_MILVUS_COLLECTION_OLD))
    embedding2 = torch.tensor(
        MU.query_vectors_by_ids(ids=[tail_entity_id], collection_name=RemoteMilvus.TEST_MILVUS_COLLECTION_OLD))
    print(embedding1)
    print(embedding2)
    # operation
    operator_result = ComplexDiagonalDynamicOperator(embedding2, relation_real, relation_imag, 256)

    # comparison
    pos_scores = DotComparator(embedding1, operator_result)

    print(pos_scores)
