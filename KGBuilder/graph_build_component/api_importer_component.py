#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import tqdm
from kgdt.neo4j.creator import NodeBuilder
from kgdt.pipeline.component.base import Component

from definitions import CodeConstant
from graph_build_component.ConstantCodeEntity import CodeEntityCategory, CodeEntityRelationCategory

from script.code_kg_builder import CodeElementGraphDataBuilder

from kgdt.models.graph import GraphData
from kgdt.models.doc import MultiFieldDocumentCollection, MultiFieldDocument

from graph_build_component.html_extracter import HtmlExtractor

# from component.spacy_model import spacy_model

"""
API知识图谱构建的主要功能实现类，通过创建api_importer_component类的实例可以将传入的JAVA源码解析结果构建成知识图谱。
"""


def search_field_id_dict(f_c_list, f_id):
    for line in f_c_list:
        if line["end_name"] == str(f_id):
            return line["start_name"]
    return None


class APIImporterComponent(Component):
    LABEL_CODE_ELEMENT = "code_element"
    SUPPORT_LANGUAGE_JAVA = "java"

    def provided_entities(self):
        entity_labels = set()
        entity_labels.add(APIImporterComponent.LABEL_CODE_ELEMENT)
        category_codes = CodeEntityCategory.category_code_to_str_list_map.keys()
        for category_code in category_codes:
            entity_labels.update(set(CodeEntityCategory.to_str_list(category_code)))
        return entity_labels
        # TODO: add interface for the constant

    def dependent_entities(self):
        return set()

    def provided_relations(self):
        relations = set()
        category_codes = CodeEntityRelationCategory.category_code_to_str_map.keys()
        for category_code in category_codes:
            relations.add(CodeEntityRelationCategory.to_str(category_code))
        return relations
        # TODO: add interface for the constant

    def dependent_relations(self):
        return set()

    def provided_document_fields(self):
        return set()

    def dependent_document_fields(self):
        return set()

    def __init__(self, package_entity_json_name, class_entity_json_name, method_entity_json_name,
                 field_entity_json_name, relation_json_name, field_class_relation_json_name, graph_data=None,
                 doc_collection=None, pro_name=None, do_import_primary_type=True, language=SUPPORT_LANGUAGE_JAVA,
                 library_name=None):
        super().__init__(graph_data, doc_collection)
        with open(class_entity_json_name, "r", encoding="utf-8", errors="ignore") as f:
            self.class_entity_list = json.load(f)
        with open(method_entity_json_name, "r", encoding="utf-8", errors="ignore") as f:
            self.method_entity_list = json.load(f)
        with open(field_entity_json_name, "r", encoding="utf-8", errors="ignore") as f:
            self.field_entity_list = json.load(f)
        with open(package_entity_json_name, "r", encoding="utf-8", errors="ignore") as f:
            self.package_entity_list = json.load(f)
        with open(relation_json_name, "r", encoding="utf-8", errors="ignore") as f:
            self.relations_list = json.load(f)
        with open(field_class_relation_json_name, "r", encoding="utf-8", errors="ignore") as f:
            self.field_class_relation_list = json.load(f)
        self.return_value_entity_list = []
        self.exception_value_entity_list = []
        self.parameter_entity_list = []
        self.do_import_primary_type = do_import_primary_type

        self.pro_name = pro_name
        self.code_element_kg_builder = CodeElementGraphDataBuilder(self.graph_data)
        self.language = language
        self.library_name = library_name
        # self.nlp = spacy_model()

    def run(self, g_path, d_path):
        print("running component %r" % (self.type()))

        # primary_name_to_node_id_map = self.import_primary_type()
        # self.save(g_path=g_path, d_path=d_path)
        package_name_to_node_id_map = self.import_entity_from_package_list()
        self.save(g_path=g_path, d_path=d_path)
        class_name_to_node_id_map = self.import_entity_from_class_list()
        self.save(g_path=g_path, d_path=d_path)
        method_name_to_node_id_map = self.import_entity_from_method_list(class_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        field_id_to_node_id_map = self.import_entity_from_field_list(class_name_to_node_id_map, )
        self.save(g_path=g_path, d_path=d_path)
        param_name_to_node_id_map = self.import_param_entity_from_method_list(method_name_to_node_id_map,
                                                                              class_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        return_name_to_node_id_map = self.import_return_entity(method_name_to_node_id_map, class_name_to_node_id_map,
                                                               )
        self.save(g_path=g_path, d_path=d_path)
        exception_name_to_node_id_map = self.import_exception_entity(method_name_to_node_id_map,
                                                                     class_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.package_class_relations(package_name_to_node_id_map, class_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.import_inherit_info(class_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.build_aliases()
        self.save(g_path=g_path, d_path=d_path)
        self.add_class_field(class_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.add_field_value_field(field_id_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.add_method_field(method_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.add_param_field(method_name_to_node_id_map, param_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.add_return_value_field(method_name_to_node_id_map, return_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)
        self.add_exception_condition_field(method_name_to_node_id_map, exception_name_to_node_id_map)
        self.save(g_path=g_path, d_path=d_path)

    def package_class_relations(self, package_name_to_node_id_map, class_name_to_node_id_map):
        print("Import package class relation info")
        relations = []
        error_num = 0
        for r in tqdm.tqdm(self.relations_list):
            try:
                if r["relation_type"] == 1:
                    start_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + r["start_name"],
                                                                     package_name_to_node_id_map)
                    end_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + r["end_name"],
                                                                   class_name_to_node_id_map)
                    if start_id is None or end_id is None:
                        error_num += 1
                        continue
                    relation_type = CodeEntityRelationCategory.RELATION_CATEGORY_BELONG_TO
                    relations.append([start_id, end_id, relation_type])
                elif r["relation_type"] == 2:
                    start_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + r["start_name"],
                                                                     package_name_to_node_id_map)
                    end_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + r["end_name"],
                                                                   class_name_to_node_id_map)
                    if start_id is None or end_id is None:
                        error_num += 1
                        continue
                    relation_type = CodeEntityRelationCategory.RELATION_CATEGORY_EXTENDS
                    relations.append([start_id, end_id, relation_type])
                else:
                    start_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + r["start_name"],
                                                                     package_name_to_node_id_map)
                    end_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + r["end_name"],
                                                                   class_name_to_node_id_map)
                    if start_id is None or end_id is None:
                        error_num += 1
                        continue
                    relation_type = CodeEntityRelationCategory.RELATION_CATEGORY_IMPLEMENTS
                    relations.append([start_id, end_id, relation_type])
            except:
                error_num += 1

        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("%s times error in package class relation info import" % error_num)
        print("end import package class relation info")
        print()

    def import_entity_from_method_list(self, class_name_to_node_id_map):
        print("start import method node from list")
        entity_name_to_node_id_map = {}
        relations = []
        error_num_1 = 0
        error_num_2 = 0
        for entity_info_row in tqdm.tqdm(self.method_entity_list):
            if entity_info_row is None:
                continue
            full_des = HtmlExtractor.html_remove(entity_info_row.get("description", ""))
            api_entity_json = {"qualified_name": self.library_name + '%' + entity_info_row["methodName"],
                               "simple_qualified_name": entity_info_row["methodName"],
                               "api_id": self.graph_data.max_node_id,
                               "api_type": CodeEntityCategory.CATEGORY_METHOD,
                               "full_description": full_des,
                               }
            format_qualified_name = self.code_element_kg_builder.format_qualified_name(
                api_entity_json[CodeConstant.QUALIFIED_NAME])
            if format_qualified_name:
                node_id = self.import_normal_entity(api_entity_json)
                entity_name_to_node_id_map[format_qualified_name] = node_id
                if "belongClass" not in entity_info_row or entity_info_row["belongClass"] == "":
                    parent_name = "java.lang.Object"
                else:
                    parent_name = self.library_name + '%' + self.code_element_kg_builder.format_qualified_name(
                        entity_info_row["belongClass"])
                parent_id = self.get_graph_node_by_qualified_name(parent_name, class_name_to_node_id_map)
                if parent_id is None or parent_name is None:
                    # print("ERROR: belongClass is not in class_list", parent_name)
                    error_num_2 += 1
                else:
                    temp_r = [node_id, parent_id, CodeEntityRelationCategory.RELATION_CATEGORY_BELONG_TO]
                    relations.append(temp_r)
            else:
                error_num_1 += 1
        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("%s times error in method import" % error_num_1)
        print("%s times errot in method belong to relation import" % error_num_2)
        print("end import from method list")
        return entity_name_to_node_id_map

    def import_entity_from_class_list(self):
        print("start import class node from list")
        entity_name_to_node_id_map = {}
        error_num = 0
        for entity_info_row in tqdm.tqdm(self.class_entity_list):
            if entity_info_row is None:
                continue
            if entity_info_row["type"]:
                api_type = CodeEntityCategory.CATEGORY_INTERFACE
            else:
                api_type = CodeEntityCategory.CATEGORY_CLASS
            api_entity_json = {"qualified_name": self.library_name + '%' + entity_info_row["name"],
                               "simple_qualified_name": entity_info_row["name"],
                               "api_id": self.graph_data.max_node_id,
                               "api_type": api_type,
                               }
            format_qualified_name = self.code_element_kg_builder.format_qualified_name(
                api_entity_json[CodeConstant.QUALIFIED_NAME])
            if format_qualified_name:
                node_id = self.import_normal_entity(api_entity_json)
                entity_name_to_node_id_map[format_qualified_name] = node_id
            else:
                # print("Without qualified_name", entity_info_row)
                error_num += 1
        self.graph_data.print_graph_info()
        print("%s times error in class import" % error_num)
        print("end import from class list")
        print()
        return entity_name_to_node_id_map

    def import_entity_from_field_list(self, class_name_to_node_id_map):
        primary_name_to_node_id_map = {}
        print("start import field node from list")
        field_id_to_node_id = {}
        relations = []
        error_num_1 = 0
        error_num_2 = 0
        for entity_info_row in tqdm.tqdm(self.field_entity_list):
            if entity_info_row is None:
                continue
            api_type = CodeEntityCategory.CATEGORY_FIELD_OF_CLASS
            full_des = HtmlExtractor.html_remove(entity_info_row["comment"])
            class_name = search_field_id_dict(self.field_class_relation_list, entity_info_row["id"])
            if class_name is None:
                error_num_1 += 1
                continue
            class_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + class_name,
                                                             class_name_to_node_id_map)
            if class_id is None:
                error_num_1 += 1
                continue
            temp = entity_info_row["full_declaration"].split("=")
            if len(temp) == 2:
                full_declaration = temp[0].strip()
            else:
                full_declaration = entity_info_row["full_declaration"]
            type_name = self.library_name + '%' + entity_info_row["field_type"]
            if type_name == "":
                type_name = "java.lang.Object"
            api_entity_json = {
                "qualified_name": self.library_name + '%' + class_name + "." + entity_info_row["field_name"],
                "simple_qualified_name": class_name + "." + entity_info_row["field_name"],
                "full_declaration": full_declaration,
                "api_id": self.graph_data.max_node_id,
                "api_type": api_type,
                "type": type_name,
                "full_description": full_des,
                "value_name": entity_info_row["field_name"],
            }
            node_id = self.import_normal_entity(api_entity_json)
            field_id_to_node_id[entity_info_row["id"]] = node_id
            # 检查当前名字是否已经在graphdata中出现过,以此来添加type of 关系
            type_id = self.get_graph_node_by_qualified_name(type_name, class_name_to_node_id_map)
            if type_id is None and type_name not in primary_name_to_node_id_map.keys():
                # print("ERROR: type Class is not in class_list", type_name)
                error_num_2 += 1
                continue
            else:
                temp_r = [node_id, type_id, CodeEntityRelationCategory.RELATION_CATEGORY_TYPE_OF]
                relations.append(temp_r)
            temp_r = [class_id, node_id, CodeEntityRelationCategory.RELATION_CATEGORY_HAS_FIELD]
            relations.append(temp_r)
        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("%s field not in class" % error_num_1)
        print("%s times error in field type of relation import because type class loss" % error_num_2)
        print("end import from class list")
        print()
        return field_id_to_node_id

    def import_entity_from_package_list(self):
        """
        从文件中读取所有的Package实体，添加到graphData当中
        """
        print("start package node from list")
        # 未成功数
        error_num_1 = 0
        # 成功但重复数
        error_num_2 = 0
        entity_name_to_node_id_map = {}
        for entity_info_row in tqdm.tqdm(self.package_entity_list):
            if entity_info_row is None:
                continue
            api_entity_json = {
                "qualified_name": self.library_name + '%' + entity_info_row["qualified_name"],
                "simple_qualified_name": entity_info_row["qualified_name"],
                "api_id": self.graph_data.max_node_id,
                "api_type": CodeEntityCategory.CATEGORY_PACKAGE
            }
            format_qualified_name = self.code_element_kg_builder.format_qualified_name(
                api_entity_json[CodeConstant.QUALIFIED_NAME])
            if format_qualified_name:
                if format_qualified_name in entity_name_to_node_id_map.keys():
                    error_num_2 += 1
                node_id = self.import_normal_entity(api_entity_json)
                entity_name_to_node_id_map[format_qualified_name] = node_id
            else:
                error_num_1 += 1
        self.graph_data.print_graph_info()
        print("%s times errors in package import" % error_num_1)
        print("%s times read same package" % error_num_2)
        print("end import from package list")
        return entity_name_to_node_id_map

    def import_param_entity_from_method_list(self, method_name_to_node_id_map, class_name_to_node_id_map):
        print("start import param node from method list")
        entity_name_to_node_id_map = {}
        relations = []
        error_num_1 = 0
        error_num_2 = 0
        for entity_info_row in tqdm.tqdm(self.method_entity_list):
            if entity_info_row is None:
                continue
            method_name = self.code_element_kg_builder.format_qualified_name(entity_info_row["methodName"])
            method_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + method_name,
                                                              method_name_to_node_id_map)
            if method_id is None:
                error_num_1 += 1
            else:
                param_qualified_name = dict()
                for index, param in enumerate(entity_info_row["parameter"]):
                    p = param.split(" ")
                    p = [" ".join(p[:len(p) - 1]), p[-1]]
                    param_qualified_name[p[-1]] = (index, method_name + ".<P>" + p[-1])
                    for row in entity_info_row["paramsTag"]:
                        if row["key"] not in param_qualified_name.keys():
                            param_qualified_name[row["key"]] = (-1, method_name + ".<P>" + row["key"])
                for param in param_qualified_name.keys():
                    short_description = ""
                    for row in entity_info_row["paramsTag"]:
                        if row["key"] == param:
                            short_description = row["value"]
                    param_type = ""
                    if param_qualified_name[param][0] != -1:
                        param_type = entity_info_row["parameterTypeList"][param_qualified_name[param][0]].strip()

                    api_entity_json = {
                        "qualified_name": self.library_name + '%' + param_qualified_name[param][1],
                        "simple_qualified_name": param_qualified_name[param][1],
                        "simple_name": param,
                        "type": param_type,
                        "value_name": param_qualified_name[param][0],
                        "short_description": short_description,
                        "api_type": CodeEntityCategory.CATEGORY_PARAMETER}
                    param_id = self.import_abstract_entity(api_entity_json)
                    temp_r = [method_id, param_id, CodeEntityRelationCategory.RELATION_CATEGORY_HAS_PARAMETER]
                    relations.append(temp_r)
                    entity_name_to_node_id_map[self.library_name + '%' + param_qualified_name[param][1]] = param_id
                    if param_qualified_name[param][0] != -1:
                        type_name = self.library_name + '%' + self.code_element_kg_builder.format_qualified_name(
                            param_type)
                        node_id = self.get_graph_node_by_qualified_name(type_name, class_name_to_node_id_map)
                        if node_id is not None:
                            temp_r = [param_id, node_id, CodeEntityRelationCategory.RELATION_CATEGORY_TYPE_OF]
                            relations.append(temp_r)
                        else:
                            # print("The param node type %s not in the class map" % param_type)
                            error_num_2 += 1
        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("%s times error in method visit" % error_num_1)
        print("%s times error in param type of relation import" % error_num_2)
        print("end import param node from method list")
        return entity_name_to_node_id_map

    def import_return_entity(self, method_name_to_node_id_map, class_name_to_node_id_map, ):
        print("start import return value node from method list")
        entity_name_to_node_id_map = {}
        relations = []
        error_num_1 = 0
        error_num_2 = 0
        for entity_info_row in tqdm.tqdm(self.method_entity_list):
            try:
                if entity_info_row is None:
                    continue
                method_name = self.code_element_kg_builder.format_qualified_name(entity_info_row["methodName"])
                method_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + method_name,
                                                                  method_name_to_node_id_map)
                if method_id is None:
                    error_num_1 += 1
                else:
                    if "returnValueType" not in entity_info_row:
                        continue
                    if "returnValueDescription" not in entity_info_row:
                        continue

                    api_entity_json = {
                        "qualified_name": self.library_name + '%' + method_name + ".<R>",
                        "simple_qualified_name": method_name + ".<R>",
                        "simple_name": entity_info_row["returnValueType"],
                        "type": entity_info_row["returnValueType"],
                        "value_name": "<R>",
                        "description": entity_info_row["returnValueDescription"],
                        "api_type": CodeEntityCategory.CATEGORY_RETURN_VALUE,
                    }
                    return_id = self.import_abstract_entity(api_entity_json)
                    temp_r = [method_id, return_id, CodeEntityRelationCategory.RELATION_CATEGORY_HAS_RETURN_VALUE]
                    relations.append(temp_r)
                    entity_name_to_node_id_map[method_name + ".<R>"] = return_id
                    type_name = self.library_name + '%' + api_entity_json["type"]
                    type_id = self.get_graph_node_by_qualified_name(type_name, class_name_to_node_id_map)
                    if type_id is not None:
                        temp_r = [return_id, type_id, CodeEntityRelationCategory.RELATION_CATEGORY_TYPE_OF]
                        relations.append(temp_r)
                    else:
                        error_num_2 += 1

                    # 添加 return code directive 实体和关系
                    if "returnCodeDirective" in entity_info_row.keys():
                        if entity_info_row["returnCodeDirective"] != "":
                            count = 0
                            for row in entity_info_row["returnCodeDirective"]:
                                code_directive = row["value"]
                                api_entity_json = {
                                    "qualified_name": self.library_name + '%' + method_name + ".<R>." + row[
                                        "key"] + ".code_directive" + "." + str(count),
                                    "simple_qualified_name": method_name + ".<R>." + row[
                                        "key"] + ".code_directive" + "." + str(count),
                                    "simple_name": row["key"] + "." + str(count),
                                    "description": code_directive,
                                    "type": row["key"],
                                    "value_name": "<R>." + row["key"] + ".code_directive",
                                    "api_type": CodeEntityCategory.CATEGORY_RETURN_CODE_DIRECTIVE,
                                }

                                code_directive_id = self.import_normal_entity(api_entity_json)
                                entity_name_to_node_id_map[
                                    self.library_name + '%' +
                                    method_name + ".<R>." + row["key"] + ".code_directive." + str(count)] \
                                    = code_directive_id
                                temp_r = [method_id, code_directive_id,
                                          CodeEntityRelationCategory.RELATION_CATEGORY_HAS_RETURN_CODE_DIRECTIVE]
                                relations.append(temp_r)
                                count += 1
                        else:
                            error_num_2 += 1
            except:
                error_num_2 += 1

        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("%s times error in method visit" % error_num_1)
        print("%s times error in return value type of relation import" % error_num_2)
        print("end import return value node from method list")
        return entity_name_to_node_id_map

    def import_exception_entity(self, method_name_to_node_id_map, class_name_to_node_id_map):
        print("start import exception condition node from method list")
        entity_name_to_node_id_map = {}
        relations = []
        error_num_1 = 0
        error_num_2 = 0
        for entity_info_row in tqdm.tqdm(self.method_entity_list):
            if entity_info_row is None:
                continue
            method_name = self.code_element_kg_builder.format_qualified_name(entity_info_row["methodName"])
            method_id = self.get_graph_node_by_qualified_name(self.library_name + '%' + method_name,
                                                              method_name_to_node_id_map)
            if method_id is None:
                error_num_1 += 1
            else:
                short_name_set = []
                for index, exception_name in enumerate(entity_info_row["throwException"]):
                    throw_info = ""
                    short_name = exception_name.split(".")[-1]
                    short_name_set.append(short_name)
                    for row in entity_info_row["throwsTag"]:
                        if row["key"] == short_name:
                            throw_info = row["value"]
                    api_entity_json = {
                        "qualified_name": self.library_name + '%' + method_name + "." + exception_name,
                        "simple_qualified_name": method_name + "." + exception_name,
                        "short_description": throw_info,
                        "api_type": CodeEntityCategory.CATEGORY_EXCEPTION_CONDITION,
                    }
                    exception_id = self.import_normal_entity(api_entity_json)
                    entity_name_to_node_id_map[
                        self.library_name + '%' + method_name + "." + exception_name] = exception_id
                    temp_r = [method_id, exception_id,
                              CodeEntityRelationCategory.RELATION_CATEGORY_HAS_EXCEPTION_CONDITION]
                    relations.append(temp_r)
                    type_id = self.get_graph_node_by_qualified_name(exception_name, class_name_to_node_id_map)
                    if type_id is None:
                        error_num_2 += 1
                    else:
                        temp_r = [exception_id, type_id, CodeEntityRelationCategory.RELATION_CATEGORY_TYPE_OF]
                        relations.append(temp_r)
                for row in entity_info_row["throwsTag"]:
                    if row["key"] not in short_name_set:
                        throw_info = row["value"]
                        api_entity_json = {
                            "qualified_name": self.library_name + '%' + method_name + "." + row["key"],
                            "simple_qualified_name": method_name + "." + row["key"],
                            "short_description": throw_info,
                            "api_type": CodeEntityCategory.CATEGORY_EXCEPTION_CONDITION,
                        }
                        exception_id = self.import_normal_entity(api_entity_json)
                        entity_name_to_node_id_map[
                            self.library_name + '%' + method_name + "." + row["key"]] = exception_id
                        temp_r = [method_id, exception_id,
                                  CodeEntityRelationCategory.RELATION_CATEGORY_HAS_EXCEPTION_CONDITION]
                        relations.append(temp_r)
                # 插入code directive
                if "throwsCodeDirective" in dict(entity_info_row).keys():
                    if entity_info_row["throwsCodeDirective"] != "":
                        for row in entity_info_row["throwsCodeDirective"]:
                            code_directive = row["value"]
                            api_entity_json = {
                                "qualified_name": self.library_name + '%' + method_name + "." + row[
                                    "key"] + "." + "code_directive",
                                "simple_qualified_name": method_name + "." + row["key"] + "." + "code_directive",
                                "short_description": code_directive,
                                "api_type": CodeEntityCategory.CATEGORY_EXCEPTION_CODE_DIRECTIVE,
                            }
                            code_directive_id = self.import_normal_entity(api_entity_json)
                            entity_name_to_node_id_map[
                                self.library_name + '%' + method_name + "." + row["key"] + "." + "code_directive"] \
                                = code_directive_id
                            temp_r = [method_id, code_directive_id,
                                      CodeEntityRelationCategory.RELATION_CATEGORY_HAS_EXCEPTION_CODE_DIRECTIVE]
                            relations.append(temp_r)

                    else:
                        error_num_2 += 1
        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("%s times error in method visit" % error_num_1)
        print("%s times error in exception type of relation import" % error_num_2)
        print("end import exception condition node from method list")
        return entity_name_to_node_id_map

    def import_normal_entity(self, api_entity_json):
        format_qualified_name = self.code_element_kg_builder.format_qualified_name(
            api_entity_json[CodeConstant.QUALIFIED_NAME])

        if not format_qualified_name:
            # print("ERROR: API without qualified name.\n" % api_entity_json)
            return
        api_entity_json.pop(CodeConstant.QUALIFIED_NAME)
        node_id = self.code_element_kg_builder.add_normal_code_element_entity(format_qualified_name,
                                                                              api_entity_json["api_type"],
                                                                              **api_entity_json)
        return node_id

    def import_abstract_entity(self, api_entity_json):
        format_qualified_name = api_entity_json[CodeConstant.QUALIFIED_NAME]
        api_entity_json.pop(CodeConstant.QUALIFIED_NAME)
        node_id = self.code_element_kg_builder.add_normal_code_element_entity(format_qualified_name,
                                                                              api_entity_json["api_type"],
                                                                              **api_entity_json)
        return node_id

    def add_primary_type(self, primary_type_name, **properties):
        """
        添加一些默认的基础数据类型
        """
        properties[CodeConstant.QUALIFIED_NAME] = primary_type_name

        cate_labels = CodeEntityCategory.to_str_list(CodeEntityCategory.CATEGORY_PRIMARY_TYPE)
        builder = NodeBuilder()
        builder = builder.add_property(**properties).add_entity_label().add_labels(
            APIImporterComponent.LABEL_CODE_ELEMENT, *cate_labels)
        node_id = self.graph_data.add_node(
            node_id=GraphData.UNASSIGNED_NODE_ID,
            node_labels=builder.get_labels(),
            node_properties=builder.get_properties(),
            primary_property_name=CodeConstant.QUALIFIED_NAME)
        return node_id

    def import_primary_type(self):
        print("import primary_type")
        type_list = []
        entity_name_to_id_map = {}
        if self.language == APIImporterComponent.SUPPORT_LANGUAGE_JAVA:
            type_list = CodeEntityCategory.java_primary_types()

        for item in tqdm.tqdm(type_list):
            code_element = {
                CodeConstant.QUALIFIED_NAME: item["name"],
                "api_type": CodeEntityCategory.CATEGORY_PRIMARY_TYPE,
                "short_description": item["description"]
            }
            node_id = self.add_primary_type(item["name"], **code_element)
            entity_name_to_id_map[item["name"]] = node_id
        self.graph_data.print_label_count()
        return entity_name_to_id_map

    def import_inherit_info(self, class_name_to_node_id_map):
        print("start inherit info")
        relations = []
        error_num_1 = 0
        error_num_2 = 0
        for entity_info_row in tqdm.tqdm(self.class_entity_list):
            try:
                if entity_info_row is None:
                    continue
                format_qualified_name = self.code_element_kg_builder.format_qualified_name(self.library_name + "%" +
                                                                                           entity_info_row["name"])
                node_id = self.get_graph_node_by_qualified_name(format_qualified_name, class_name_to_node_id_map)
                if node_id is None:
                    error_num_1 += 1
                else:
                    node_label = self.graph_data.get_node_info_dict(node_id)["labels"]
                    if "interface" in list(node_label):
                        r_type = CodeEntityRelationCategory.RELATION_CATEGORY_IMPLEMENTS
                    else:
                        r_type = CodeEntityRelationCategory.RELATION_CATEGORY_EXTENDS
                    for p_name in entity_info_row["inherit"]:
                        parent_id = self.get_graph_node_by_qualified_name(p_name, class_name_to_node_id_map)
                        if parent_id is not None:
                            temp_r = [node_id, parent_id, r_type]
                            relations.append(temp_r)
                        else:
                            error_num_2 += 1
            except:
                error_num_2 += 1

        print("%s times error in class visit" % error_num_1)
        print("%s times error in class inherit relation import" % error_num_2)
        self.import_relation_from_list(relations)
        self.graph_data.print_graph_info()
        print("end import inherit info")
        print()

    def build_aliases(self):
        """
        为API添加别名信息
        """
        self.code_element_kg_builder.build_aliases_for_code_element()
        self.graph_data.refresh_indexer()

    def import_relation_from_list(self, relations):
        print("start import relation")
        self.graph_data.print_graph_info()

        for row in tqdm.tqdm(relations):
            self.graph_data.add_relation(startId=row[0],
                                         endId=row[1],
                                         relationType=CodeEntityRelationCategory.to_str(row[2]))
        print("end import relation")
        self.graph_data.print_graph_info()

    def save(self, g_path, d_path):
        self.graph_data.save(g_path)
        self.doc_collection.save(d_path)

    """
    下面的方法属于文档生成
    """

    def add_class_field(self, class_name_to_node_id_map):
        print("add class doc")
        error_num = 0
        right_num = 0
        for entity_row in tqdm.tqdm(self.class_entity_list):
            try:
                format_qualified_name = self.code_element_kg_builder.format_qualified_name(
                    self.library_name + '%' + entity_row["name"])
                node_id = self.get_graph_node_by_qualified_name(format_qualified_name, class_name_to_node_id_map)
                if node_id is None:
                    error_num += 1
                else:
                    self.add_field_in_doc_collection(node_id, format_qualified_name, entity_row["description"])
                    right_num += 0
            except:
                error_num += 1
        print("%s times error in add class doc" % error_num)
        print("successful add %s class" % right_num)
        print("end add class doc")

    def add_param_field(self, method_name_to_node_id_map, param_name_to_node_id_map):
        print("add method doc")
        error_num = 0
        right_num = 0
        for index, entity_row in tqdm.tqdm(enumerate(self.method_entity_list)):
            try:
                format_qualified_name = self.library_name + '%' + self.code_element_kg_builder.format_qualified_name(
                    entity_row["methodName"])
                node_id = self.get_graph_node_by_qualified_name(format_qualified_name, method_name_to_node_id_map)
                if node_id is None:
                    error_num += 1
                else:
                    param_qualified_name = dict()
                    for item_index, item in enumerate(entity_row["parameter"]):
                        name_slipe = item.split(" ")
                        name_slipe = [" ".join(name_slipe[:len(name_slipe) - 1]), name_slipe[-1]]
                        param_qualified_name[name_slipe[-1]] = format_qualified_name + ".<P>" + name_slipe[-1]
                    for row in entity_row["paramsTag"]:
                        if row["key"] not in param_qualified_name.keys():
                            param_qualified_name[row["key"]] = format_qualified_name + ".<P>" + row["key"]
                        format_qualified_name = param_qualified_name[row["key"]]
                        node_id = self.get_graph_node_by_qualified_name(format_qualified_name,
                                                                        param_name_to_node_id_map)
                        self.add_field_in_doc_collection(node_id, format_qualified_name, row["value"])
                        right_num += 1
            except:
                error_num += 1
        print("%s times error in method visit" % error_num)
        print("successful add %s param" % right_num)
        print("end add param doc")

    def add_return_value_field(self, method_name_to_node_id_map, return_name_to_node_id_map):
        print("add method doc")
        error_num = 0
        right_num = 0
        for index, entity_row in tqdm.tqdm(enumerate(self.method_entity_list)):
            try:
                format_qualified_name = self.library_name + '%' + self.code_element_kg_builder.format_qualified_name(
                    entity_row["methodName"])
                return_qualified_name = format_qualified_name + ".<R>"
                node_id = self.get_graph_node_by_qualified_name(return_qualified_name, method_name_to_node_id_map)
                if node_id is None:
                    error_num += 1
                else:
                    return_qualified_name = format_qualified_name + ".<R>"
                    if entity_row["returnValueDescription"] != "":
                        node_id = self.get_graph_node_by_qualified_name(return_qualified_name,
                                                                        return_name_to_node_id_map)
                        self.add_field_in_doc_collection(node_id, return_qualified_name,
                                                         entity_row["returnValueDescription"])
                        right_num += 1

                    # 添加code directive相关的文档
                    if "returnCodeDirective" in entity_row.keys():
                        if entity_row["returnCodeDirective"] != "":
                            count = 0
                            for row in entity_row["returnCodeDirective"]:
                                return_code_directive_name = format_qualified_name + ".<R>." + row[
                                    "key"] + ".code_directive" + "." + str(count)
                                node_id = self.get_graph_node_by_qualified_name(return_code_directive_name,
                                                                                return_name_to_node_id_map)
                                self.add_field_in_doc_collection(node_id, return_code_directive_name, row["value"])
                                count += 1
                                right_num += 1
                        else:
                            error_num += 1
            except:
                error_num += 1
        print("%s times error in method visit" % error_num)
        print("successful add %s return value" % right_num)
        print("end add return value doc")

    def add_exception_condition_field(self, method_name_to_node_id_map, exception_name_to_node_id_map):
        print("add method doc")
        error_num = 0
        right_num = 0
        for index, entity_row in tqdm.tqdm(enumerate(self.method_entity_list)):
            try:
                format_qualified_name = self.library_name + '%' + self.code_element_kg_builder.format_qualified_name(
                    entity_row["methodName"])
                node_id = self.get_graph_node_by_qualified_name(format_qualified_name, method_name_to_node_id_map)
                if node_id is None:
                    error_num += 1
                else:
                    throw_qualified_name = dict()
                    for item_index, item in enumerate(entity_row["throwException"]):
                        short_name = item.split(".")[-1]
                        throw_qualified_name[short_name] = format_qualified_name + "." + item
                    for row in entity_row["throwsTag"]:
                        if row["key"] not in throw_qualified_name.keys():
                            throw_qualified_name[row["key"]] = format_qualified_name + "." + row["key"]
                        node_id = self.get_graph_node_by_qualified_name(throw_qualified_name[row["key"]],
                                                                        exception_name_to_node_id_map)
                        self.add_field_in_doc_collection(node_id, throw_qualified_name[row["key"]], row["value"])
                        right_num += 1
                    # 添加code directive相关的文档
                    if "throwsCodeDirective" in entity_row.keys():
                        for row in entity_row["throwsCodeDirective"]:
                            exception_code_directive_name = format_qualified_name + "." + row[
                                "key"] + "." + "code_directive"
                            node_id = self.get_graph_node_by_qualified_name(exception_code_directive_name,
                                                                            exception_name_to_node_id_map)
                            self.add_field_in_doc_collection(node_id, exception_code_directive_name, row["value"])
            except:
                error_num += 1
        print("%s times error in method visit" % error_num)
        print("successful add %s exception condition" % right_num)
        print("end add exception condition doc")

    def add_method_field(self, method_name_to_node_id_map):
        print("add method doc")
        error_num = 0
        right_num = 0
        for index, entity_row in tqdm.tqdm(enumerate(self.method_entity_list)):
            try:
                format_qualified_name = self.library_name + '%' + self.code_element_kg_builder.format_qualified_name(
                    entity_row["methodName"])
                node_id = self.get_graph_node_by_qualified_name(format_qualified_name, method_name_to_node_id_map)
                if node_id is None:
                    error_num += 1
                else:
                    if "description" in entity_row.keys():
                        node_id = method_name_to_node_id_map[format_qualified_name]
                        doc = MultiFieldDocument(id=node_id, name=entity_row["name"])
                        doc.add_field("full_html_description", entity_row["description"])
                        doc.add_field("full_description", HtmlExtractor.html_remove(entity_row["description"]))
                        # sentence_list = self.sentence_cut(HtmlExtractor.html_remove(entity_row["description"]))
                        # doc.add_field("sentence_description", sentence_list)
                        self.doc_collection.add_document(doc)
                        right_num += 1
            except:
                error_num += 1
        print("%s times error in method visit" % error_num)
        print("successful add %s method" % right_num)
        print("end add exception condition doc")

    def add_field_value_field(self, field_id_to_node_id_map):
        print("add method doc")
        error_num = 0
        right_num = 0
        for entity_row in tqdm.tqdm(self.field_entity_list):
            try:
                if entity_row["id"] not in field_id_to_node_id_map.keys():
                    error_num += 1
                else:
                    node_id = field_id_to_node_id_map[entity_row["id"]]
                    class_name = search_field_id_dict(self.field_class_relation_list, entity_row["id"])
                    format_qualified_name = class_name + "." + entity_row["field_name"]
                    self.add_field_in_doc_collection(node_id, format_qualified_name, entity_row["comment"])
                    right_num += 1
            except:
                error_num += 1
        print("%s field not in class" % error_num)
        print("successful add %s field" % right_num)
        print("end add field doc")

    def add_field_in_doc_collection(self, node_id, entity_full_qualified_name, full_html_description):
        """
        增加method相关的节点
        :param node_id:
        :param entity_full_qualified_name:
        :param full_html_description:
        :return:
        """
        # 迁移到 parser
        doc = MultiFieldDocument(id=node_id, name=entity_full_qualified_name)
        doc.add_field("full_html_description", full_html_description)
        doc.add_field("full_description", HtmlExtractor.html_remove(full_html_description))
        # sentence_list = self.sentence_cut(HtmlExtractor.html_remove(full_html_description))
        # doc.add_field("sentence_description", sentence_list)
        self.doc_collection.add_document(doc)

    def sentence_cut(self, doc_text):
        doc = self.nlp(doc_text)
        sentences = doc.sents
        return [item.text for item in sentences]

    def get_graph_node_by_qualified_name(self, name, node_name_to_node_id_map):
        if name is None or name == "":
            return None
        elif name in node_name_to_node_id_map.keys():
            return node_name_to_node_id_map[name]
        else:
            n_dict = self.graph_data.find_one_node_by_property(property_name="qualified_name", property_value=name)
            if n_dict is None:
                return None
            return n_dict["id"]
