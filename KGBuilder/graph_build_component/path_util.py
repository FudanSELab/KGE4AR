import os.path
from pathlib import Path
from definitions import KG_DIR


class PathUtil:

    @staticmethod
    def graph_data(pro_name, version):
        graph_data_output_dir = Path(os.path.join(KG_DIR, pro_name))
        graph_data_output_dir.mkdir(exist_ok=True, parents=True)

        graph_data_path = os.path.join(graph_data_output_dir,
                                       "{pro}.{version}.graph".format(pro=pro_name, version=version))
        return graph_data_path

    @staticmethod
    def multi_document_collection(pro_name, version):
        doc_output_dir = Path(os.path.join(KG_DIR, pro_name))
        doc_output_dir.mkdir(exist_ok=True, parents=True)
        doc_name = os.path.join(doc_output_dir, "{pro}.{v}.dc".format(pro=pro_name, v=version))
        return doc_name
