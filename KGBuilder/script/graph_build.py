import os

from graph_build_component.api_importer_component import APIImporterComponent
# from sekg.graph.exporter.graph_data import GraphData
from kgdt.models.graph import GraphData

from graph_build_component.path_util import PathUtil
from definitions import REPOSITORIES_PARSER_DIR


def graph_build(library_name, version, input_graph_data_path=None, output_graph_path=None, output_doc_path=None,
                doc_source_path=None):
    if input_graph_data_path is None:
        input_graph_data = None
    else:
        input_graph_data = GraphData.load(input_graph_data_path)

    if output_graph_path is None:
        output_graph_path = PathUtil.graph_data(library_name, version)
    if output_doc_path is None:
        output_doc_path = PathUtil.multi_document_collection(library_name, version)
    if doc_source_path is None:
        doc_source_path = REPOSITORIES_PARSER_DIR

    aic = APIImporterComponent(package_entity_json_name=os.path.join(doc_source_path, "Packages.json"),
                               class_entity_json_name=os.path.join(doc_source_path, "ClassAll.json"),
                               method_entity_json_name=os.path.join(doc_source_path, "MethodAll.json"),
                               field_entity_json_name=os.path.join(doc_source_path, "FieldsInClass.json"),
                               relation_json_name=os.path.join(doc_source_path,"ClassOrInterfaceAndPackageRelations.json"),
                               field_class_relation_json_name=os.path.join(doc_source_path,
                                                                           "FieldsAndClassRelations.json"),
                               do_import_primary_type=True,
                               graph_data=input_graph_data, library_name=library_name)
    aic.run(output_graph_path, output_doc_path)
    aic.save(output_graph_path, output_doc_path)
    print("=" * 50)
    aic.graph_data.print_graph_info()
    print("=" * 50)
    aic.graph_data.print_relation_info()
    print("=" * 50)
    aic.graph_data.print_label_count()
