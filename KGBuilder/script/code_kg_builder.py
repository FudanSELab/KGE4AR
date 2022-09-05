import re

from kgdt.models.doc import MultiFieldDocument, MultiFieldDocumentCollection
from kgdt.neo4j.creator import NodeBuilder
from kgdt.utils import catch_exception
from kgdt.models.graph import GraphData

from graph_build_component.ConstantCodeEntity import CodeEntityCategory, CodeEntityRelationCategory
from script.code import CodeElementNameUtil
from script.directive import DirectiveEntityCategory


class CodeElementGraphDataBuilder:
    VALID_IDENTITY_CHAR_SET = " ?,.QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890_()<>[]-:%"
    CHECK_CONSTANT_FILE_PATTERN = re.compile(r"[^A-Z_0-9]")

    def __init__(self, graph_data):
        self.graph_data = graph_data
        self.init_indexs()

    def init_indexs(self):
        self.graph_data.create_index_on_property("qualified_name", "short_description", "alias")

    def format_qualified_name(self, name):
        name = name.replace(", ", ",")
        for c in name:
            if c not in self.VALID_IDENTITY_CHAR_SET:
                return ""
        # todo: change this or add more judgement in here
        if "(" in name:
            start_name = name.split("(")
            if " " in start_name:
                return ""
        return name

    def parse_construct_to_javaparser_style(self, name):
        if "(" not in name:
            return name
        head = name.split("(")[0]
        tail = name.split("(")[1]

        return "{class_part}.<init>({parameter}".format(class_part=self.get_parent_name_for_api(head), parameter=tail)

    @staticmethod
    def get_simple_name_for_type(name):
        return name.split(".")[-1]

    @staticmethod
    def get_parent_name_for_api(name):
        split = name.split("(")[0].split(".")
        return ".".join(split[:-1])

    @staticmethod
    def get_parameter_num(method_name):

        if method_name.endswith("()"):
            return 0
        return method_name.count(",") + 1

    def find_match_method_by_actual_method_call(self, actual_method_call, method_nodes):
        if len(method_nodes) == 0:
            return None
        if len(method_nodes) == 1:
            return method_nodes[0]

        actual_parameter = self.get_parameter_num(actual_method_call)
        parameter_num_2_methods = {}

        for candidate_node in method_nodes:
            team = self.get_parameter_num(candidate_node["properties"]["qualified_name"])
            if team not in parameter_num_2_methods:
                parameter_num_2_methods[team] = []
            parameter_num_2_methods[team].append(candidate_node)

        if actual_parameter not in parameter_num_2_methods:
            print("match method fail for %r following candidate %r" % (
                actual_method_call,
                [candidate_node["properties"]["qualified_name"] for candidate_node in method_nodes]))

            return None

        if len(parameter_num_2_methods[actual_parameter]) > 1:
            print("match method fail for %r following candidate %r" % (
                actual_method_call,
                [candidate_node["properties"]["qualified_name"] for candidate_node in method_nodes]))

            return None

        return parameter_num_2_methods[actual_parameter][0]

    def add_base_value_entity_node(self, value_type, value_name, short_description="",
                                   entity_category=CodeEntityCategory.CATEGORY_VALUE, **extra_properties):
        qualified_name = "{type} {var_name}".format(type=value_type,
                                                    var_name=value_name)
        simple_name = "{type} {var_name}".format(type=self.get_simple_name_for_type(value_type),
                                                 var_name=value_name)
        if short_description == None:
            short_description = ""
        code_element = {
            "qualified_name": qualified_name,
            "simple_name": simple_name,
            "type": value_type,
            "value_name": value_name,
            "short_description": short_description,
        }
        for k, v in extra_properties.items():
            if k not in code_element:
                code_element[k] = v
        cat_labels = CodeEntityCategory.to_str_list(entity_category)

        builder = NodeBuilder().add_property(**code_element).add_entity_label().add_labels("code_element",
                                                                                           *cat_labels)

        new_field_node_id = self.graph_data.add_node_with_multi_primary_property(
            node_id=GraphData.UNASSIGNED_NODE_ID,
            node_labels=builder.get_labels(),
            node_properties=builder.get_properties(),
            primary_property_names=["qualified_name", "short_description"])

        type_node_id = self.add_type_node(value_type)

        self.graph_data.add_relation(new_field_node_id,
                                     CodeEntityRelationCategory.to_str(
                                         CodeEntityRelationCategory.RELATION_CATEGORY_TYPE_OF),
                                     type_node_id)

        return new_field_node_id

    def add_method_node(self, method_qualified_name, **extra_info):
        return self.add_normal_code_element_entity(qualified_name=method_qualified_name,
                                                   entity_category=CodeEntityCategory.CATEGORY_METHOD, **extra_info)

    def add_type_node(self, type_str):
        """
        add a new node stand for a type in GraphData.
        :param type_str:
        :return:
        """

        cat_label = CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_CLASS)
        builder = NodeBuilder().add_entity_label().add_labels("code_element", cat_label).add_one_property(
            "qualified_name",
            type_str)
        exist_json = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=type_str)

        if exist_json:
            return exist_json[self.graph_data.DEFAULT_KEY_NODE_ID]

        # print("add new type %s" % (type_str))

        type_node_id = self.graph_data.add_node(
            node_id=GraphData.UNASSIGNED_NODE_ID,
            node_labels=builder.get_labels(),
            node_properties=builder.get_properties(),
            primary_property_name="qualified_name")

        if type_node_id == GraphData.UNASSIGNED_NODE_ID:
            print("add new type fail: %r- %r" % (type_node_id, type_str))

        if "[]" in type_str:
            base_type_for_array = type_str.strip("[]")
            # print("array type- %s, base type- %s" % (type_str, base_type_for_array))
            base_type_node_id = self.add_type_node(base_type_for_array)

            self.graph_data.add_relation(type_node_id, "array of", base_type_node_id)

        return type_node_id

    def add_base_overrloading_method_node(self, simple_method_name):
        """
        add a new node stand for a base abstract method node. etc. java.lang.Math.abs, the method without parameters
        :param simple_method_name:  java.lang.Math.abs, the method without parameters
        :return:
        """

        cat_label = CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD)

        builder = NodeBuilder().add_entity_label().add_labels("code_element", cat_label).add_one_property(
            "qualified_name",
            simple_method_name)
        exist_json = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=simple_method_name)

        if exist_json:
            return exist_json[self.graph_data.DEFAULT_KEY_NODE_ID]

        new_node_id = self.graph_data.add_node(
            node_id=GraphData.UNASSIGNED_NODE_ID,
            node_labels=builder.get_labels(),
            node_properties=builder.get_properties(),
            primary_property_name="qualified_name")

        return new_node_id

    def add_normal_code_element_entity(self, qualified_name, entity_category, **extra_properties):
        """
        add the normal code element whose their qualified_name are unique
        :param qualified_name: the qualified_name of the code element
        :param entity_category:
        :param extra_properties:
        :return:
        """
        format_qualified_name = self.format_qualified_name(qualified_name)
        if not format_qualified_name:
            return GraphData.UNASSIGNED_NODE_ID

        code_element = {
            "qualified_name": format_qualified_name,
            "entity_category": entity_category
        }

        for k, v in extra_properties.items():
            if k not in code_element:
                code_element[k] = v

        cate_labels = CodeEntityCategory.to_str_list(entity_category)

        builder = NodeBuilder().add_entity_label().add_labels("code_element", *cate_labels).add_property(**code_element)

        node_id = self.graph_data.add_node(
            node_id=GraphData.UNASSIGNED_NODE_ID,
            node_labels=builder.get_labels(),
            node_properties=builder.get_properties(),
            primary_property_name="qualified_name")
        return node_id

    def add_normal_directive_entity(self, qualified_name, entity_category, **extra_properties):
        """
        add the normal code element whose their qualified_name are unique
        :param qualified_name: the qualified_name of the code element
        :param entity_category:
        :param extra_properties:
        :return:
        """
        format_qualified_name = self.format_qualified_name(qualified_name)
        if not format_qualified_name:
            return GraphData.UNASSIGNED_NODE_ID

        code_element = {
            "qualified_name": format_qualified_name,
            "entity_category": entity_category
        }

        for k, v in extra_properties.items():
            if k not in code_element:
                code_element[k] = v

        cate_labels = DirectiveEntityCategory.to_str_list(entity_category)

        builder = NodeBuilder().add_entity_label().add_labels("directive", *cate_labels).add_property(**code_element)

        node_id = self.graph_data.add_node(
            node_id=GraphData.UNASSIGNED_NODE_ID,
            node_labels=builder.get_labels(),
            node_properties=builder.get_properties(),
            primary_property_name="qualified_name")
        return node_id

    def add_relation_by_not_creating_entity(self, start_name, end_name, relation_type):
        start_name = self.format_qualified_name(start_name)
        end_name = self.format_qualified_name(end_name)

        if not start_name:
            print("start name not __valid, start name=%r" % start_name)
            return False
        if not end_name:
            print("end name not __valid, end name=%r" % end_name)
            return False

        start_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=start_name)
        if start_node is None:
            print("%r not found when creating relation" % start_name)
            return False

        start_node_id = start_node[GraphData.DEFAULT_KEY_NODE_ID]

        end_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                             property_value=end_name)

        if end_node is None:
            print("%r not found when creating relation" % end_name)

            return False

        end_node_id = end_node[GraphData.DEFAULT_KEY_NODE_ID]

        self.graph_data.add_relation(start_node_id,
                                     CodeEntityRelationCategory.to_str(relation_type),
                                     end_node_id)

        return True

    def add_relation_by_creating_not_exist_entity(self, start_entity_name, end_entity_name, relation_type):
        if not start_entity_name or not end_entity_name:
            print("start name or end name is None")
            return False

        relation_type_str = CodeEntityRelationCategory.to_str(relation_type)

        start_name = self.format_qualified_name(start_entity_name)
        end_name = self.format_qualified_name(end_entity_name)

        if not start_name:
            print("start name not __valid, start name=%r" % start_entity_name)
            return False
        if not end_name:
            print("end name not __valid, end name=%r" % end_entity_name)
            return False

        start_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=start_name)

        if start_node is None:
            if "(" in start_name:
                print("add new method node for %r" % start_name)
                start_node_id = self.add_method_node(method_qualified_name=start_name)

            else:
                start_node_id = self.add_type_node(start_name)
        else:
            start_node_id = start_node[GraphData.DEFAULT_KEY_NODE_ID]

        end_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                             property_value=end_name)

        if end_node is None:
            if "(" in end_name:
                print("add new method node for %r" % end_name)
                end_node_id = self.add_method_node(method_qualified_name=end_name)

            else:
                end_node_id = self.add_type_node(end_name)
        else:
            end_node_id = end_node[GraphData.DEFAULT_KEY_NODE_ID]

        self.graph_data.add_relation(start_node_id,
                                     relation_type_str,
                                     end_node_id)

        return True

    def add_method_use_class_relation(self, start_method_name, end_class_name):
        if not start_method_name or not end_class_name:
            print("start name or end name is None")
            return False
        raw_start_name = start_method_name

        relation_type_str = CodeEntityRelationCategory.to_str(
            CodeEntityRelationCategory.RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_USE_CLASS)

        start_name = self.format_qualified_name(raw_start_name)
        start_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=start_name)

        if start_node is None:
            print("fail because of start node raw=%r format=%r" % (raw_start_name, start_name))
            return False
        type_node_id = self.add_type_node(end_class_name)

        self.graph_data.add_relation(start_node[GraphData.DEFAULT_KEY_NODE_ID],
                                     relation_type_str,
                                     type_node_id)

        return True

    def add_method_call_relation(self, start_name, end_name):
        if not start_name or not end_name:
            print("start name or end name is None")
            return False
        raw_start_name = start_name

        relation_type_str = CodeEntityRelationCategory.to_str(
            CodeEntityRelationCategory.RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL_METHOD)

        start_name = self.format_qualified_name(raw_start_name)
        start_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=start_name)

        if start_node is None:
            print("fail because of start node raw=%r format=%r" % (raw_start_name, start_name))
            return False

        end_node = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                             property_value=end_name)

        if end_node is not None:
            self.graph_data.add_relation(start_node[GraphData.DEFAULT_KEY_NODE_ID],
                                         relation_type_str,
                                         end_node[GraphData.DEFAULT_KEY_NODE_ID])
            return True

        simple_name = end_name.split("(")[0] + "("
        parent_class_name = self.get_parent_name_for_api(simple_name)
        if not parent_class_name or parent_class_name == simple_name:
            return False

        method_ids = self.get_methods_belong_to_class_name(parent_class_name)

        candidate_nodes = []

        for method_id in method_ids:
            node_json = self.graph_data.get_node_info_dict(method_id)
            if simple_name not in node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["qualified_name"]:
                continue
            candidate_nodes.append(node_json)

        end_node = self.find_match_method_by_actual_method_call(end_name, candidate_nodes)

        if end_node is None:
            end_abstract_method_node_id = self.add_base_overrloading_method_node(end_name.split("(")[0])
        else:
            end_abstract_method_node_id = end_node[GraphData.DEFAULT_KEY_NODE_ID]

        self.graph_data.add_relation(start_node[GraphData.DEFAULT_KEY_NODE_ID],
                                     relation_type_str,
                                     end_abstract_method_node_id)

        return True

    def build_abstract_overloading_relation(self):
        """
        for all methods, add a abstract new node stand for the overloading method with different parameters.
        its qualified name is simple method name without parameters. eg. java.lang.Math.abs
        :return:
        """
        print("start to build abstract_overloading_relation")
        print(self.graph_data)
        self.graph_data.print_graph_info()
        METHOD_CATE_STR = CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD)

        all_method_node_id_set = self.graph_data.get_node_ids_by_label(METHOD_CATE_STR)
        finish_node_id_set = set([])

        for node_id in all_method_node_id_set:
            if node_id in finish_node_id_set:
                continue

            node_json = self.graph_data.get_node_info_dict(node_id=node_id)

            method_qualified_name = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["qualified_name"]
            if not self.format_qualified_name(method_qualified_name):
                finish_node_id_set.add(node_id)
                continue

            if "(" not in method_qualified_name:
                finish_node_id_set.add(node_id)
                continue

            base_overloading_method_simple_name = method_qualified_name.split("(")[0]
            new_base_method_node_id = self.add_base_overrloading_method_node(
                base_overloading_method_simple_name)

            finish_node_id_set.add(new_base_method_node_id)
            class_name = self.get_parent_name_for_api(base_overloading_method_simple_name)

            class_node = self.graph_data.find_one_node_by_property(
                property_name="qualified_name",
                property_value=class_name)

            if not class_node:
                continue

            candidate_method_ids_in_class = self.get_methods_belong_to_class(class_node[GraphData.DEFAULT_KEY_NODE_ID])

            for method_id in candidate_method_ids_in_class:
                candidate_method_json = self.graph_data.get_node_info_dict(method_id)
                candidate_qualified_name = candidate_method_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES][
                    "qualified_name"]

                if base_overloading_method_simple_name not in candidate_qualified_name:
                    continue
                finish_node_id_set.add(method_id)
                if method_id == new_base_method_node_id:
                    continue

                self.graph_data.add_relation(method_id,
                                             CodeEntityRelationCategory.to_str(
                                                 CodeEntityRelationCategory.RELATION_CATEGORY_METHOD_OVERLOADING),
                                             new_base_method_node_id)
        print(self.graph_data)
        self.graph_data.print_graph_info()
        print("end import abstract overloading_relation entity json")

    def build_belong_to_relation(self):
        """
        for all methods, add a abstract new node stand for the overloading method with different parameters.
        its qualified name is simple method name without parameters. eg. java.lang.Math.abs
        :return:
        """
        print("start build belong to relation")
        print(self.graph_data)
        self.graph_data.print_graph_info()

        VALID_LABELS = [

            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_FIELD_OF_CLASS),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_CLASS),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_INTERFACE),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_ENUM_CLASS),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_PACKAGE),
        ]

        add_new_parent_label = [CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD),
                                CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD),
                                CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_FIELD_OF_CLASS), ]
        for label in VALID_LABELS:
            all_node_id_set = self.graph_data.get_node_ids_by_label(label)

            for node_id in all_node_id_set:
                node_json = self.graph_data.get_node_info_dict(node_id=node_id)
                qualified_name = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["qualified_name"]
                child_node_id = node_json[GraphData.DEFAULT_KEY_NODE_ID]

                parent_qualified_name = self.get_parent_name_for_api(qualified_name)

                if not parent_qualified_name or qualified_name == parent_qualified_name:
                    continue

                parent_node_json = self.graph_data.find_one_node_by_property("qualified_name", parent_qualified_name)

                if parent_node_json is None:
                    if label in add_new_parent_label:
                        parent_node_id = self.add_type_node(parent_qualified_name)
                        print("%r can't found, creating as class" % parent_qualified_name)
                    elif label == CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_PACKAGE):
                        parent_node_id = self.add_normal_code_element_entity(qualified_name=parent_qualified_name,
                                                                             entity_category=label)
                        print("%r can't found, creating as package" % parent_qualified_name)
                    elif parent_qualified_name == parent_qualified_name.lower():
                        if ".." in parent_qualified_name:
                            continue
                        parent_node_id = self.add_normal_code_element_entity(qualified_name=parent_qualified_name,
                                                                             entity_category=CodeEntityCategory.CATEGORY_PACKAGE)
                        print("%r can't found, creating as package" % parent_qualified_name)

                    else:
                        print("%r can't found" % parent_qualified_name)
                        continue
                else:
                    parent_node_id = parent_node_json[GraphData.DEFAULT_KEY_NODE_ID]

                self.graph_data.add_relation(child_node_id,
                                             CodeEntityRelationCategory.to_str(
                                                 CodeEntityRelationCategory.RELATION_CATEGORY_BELONG_TO),
                                             parent_node_id)

        print(self.graph_data)
        self.graph_data.print_graph_info()
        print("end build belong to relation")

    def build_value_subclass_relation(self):
        # todo: this is not useful, remove this part
        """
        for all methods, add a abstract new node stand for the overloading method with different parameters.
        its qualified name is simple method name without parameters. eg. java.lang.Math.abs
        :return:
        """
        print("start build value subclass relation")
        print(self.graph_data)
        self.graph_data.print_graph_info()

        all_node_id_set = self.graph_data.get_node_ids()
        finish_node_id_set = set([])

        VALUE_CAT_STR = CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_VALUE)

        for node_id in all_node_id_set:
            if node_id in finish_node_id_set:
                continue

            node_json = self.graph_data.get_node_info_dict(node_id=node_id)
            finish_node_id_set.add(node_id)

            if VALUE_CAT_STR not in node_json[GraphData.DEFAULT_KEY_NODE_LABELS]:
                continue

            parameter_qualified_name = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["qualified_name"]

            short_description = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["short_description"]
            value_type = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["type"]
            value_name = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["value_name"]

            if not short_description:
                base_value_node_id = self.add_base_value_entity_node(value_type=value_type,
                                                                     value_name=value_name,
                                                                     short_description="",
                                                                     entity_category=CodeEntityCategory.CATEGORY_VALUE)
            else:
                base_value_node_id = node_json[GraphData.DEFAULT_KEY_NODE_ID]

            finish_node_id_set.add(base_value_node_id)

            candidate_nodes = self.graph_data.find_nodes_by_property(
                property_name="qualified_name", property_value=parameter_qualified_name)

            for candidate_node in candidate_nodes:
                team_method_node_id = candidate_node[GraphData.DEFAULT_KEY_NODE_ID]
                if team_method_node_id in finish_node_id_set:
                    continue
                finish_node_id_set.add(team_method_node_id)
                if team_method_node_id == base_value_node_id:
                    continue

                self.graph_data.add_relation(team_method_node_id,
                                             CodeEntityRelationCategory.to_str(
                                                 CodeEntityRelationCategory.RELATION_CATEGORY_SUBCLASS_OF),
                                             base_value_node_id)

            super_base_value_node_id = self.add_base_value_entity_node(value_type=value_type,
                                                                       value_name="<V>",
                                                                       short_description="",
                                                                       entity_category=CodeEntityCategory.CATEGORY_VALUE)
            finish_node_id_set.add(super_base_value_node_id)

            self.graph_data.add_relation(base_value_node_id,
                                         CodeEntityRelationCategory.to_str(
                                             CodeEntityRelationCategory.RELATION_CATEGORY_SUBCLASS_OF),
                                         super_base_value_node_id)

        node_json = self.graph_data.find_one_node_by_properties(qualified_name="void <R>", short_description="")
        if node_json:
            self.graph_data.remove_node(node_json[GraphData.DEFAULT_KEY_NODE_ID])

        print(self.graph_data)
        self.graph_data.print_graph_info()
        print("end build value subclass relation")

    def get_methods_belong_to_class_name(self, class_qualified_name):
        class_json = self.graph_data.find_one_node_by_property(property_name="qualified_name",
                                                               property_value=class_qualified_name)
        if not class_json:
            return set([])

        class_id = class_json[GraphData.DEFAULT_KEY_NODE_ID]
        return self.get_methods_belong_to_class(class_id)

    def get_methods_belong_to_class(self, class_id):
        belong_to_relation_str = CodeEntityRelationCategory.to_str(
            CodeEntityRelationCategory.RELATION_CATEGORY_BELONG_TO)
        belong_to_relations = self.graph_data.get_relations(relation_type=belong_to_relation_str, end_id=class_id)
        valid_method_ids = set([])
        valid_method_labels = [
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD),

            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_CONSTRUCT_METHOD),

            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD),

        ]

        for (method_node_id, _, _) in belong_to_relations:

            method_node_json = self.graph_data.get_node_info_dict(method_node_id)

            for label in valid_method_labels:
                if label in method_node_json[GraphData.DEFAULT_KEY_NODE_LABELS]:
                    valid_method_ids.add(method_node_id)
                    break

        return valid_method_ids

    def get_override_method_pairs(self, start_class_id, end_class_id):
        print("start try to locate override relation between %r - %r" % (start_class_id, end_class_id))

        start_class_node_json = self.graph_data.get_node_info_dict(start_class_id)
        end_class_node_json = self.graph_data.get_node_info_dict(end_class_id)

        if not start_class_node_json:
            return []
        if not end_class_node_json:
            return []

        start_class_name = start_class_node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES][
            GraphData.DEFAULT_KEY_PROPERTY_QUALIFIED_NAME]

        end_class_name = end_class_node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES][
            GraphData.DEFAULT_KEY_PROPERTY_QUALIFIED_NAME]

        print("try to locate override relation between %r - %r" % (start_class_name, end_class_name))

        method_ids_belong_to_start_class = self.get_methods_belong_to_class(start_class_id)

        override_method_pairs = []
        for method_node_id in method_ids_belong_to_start_class:

            method_node_json = self.graph_data.get_node_info_dict(method_node_id)
            if not method_node_json:
                continue

            if CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_CONSTRUCT_METHOD) in method_node_json[
                GraphData.DEFAULT_KEY_NODE_LABELS]:
                continue
            method_qualified_name = method_node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES][
                GraphData.DEFAULT_KEY_PROPERTY_QUALIFIED_NAME]
            if ".<init>" in method_qualified_name:
                continue
            if start_class_name not in method_qualified_name:
                print("error the method name %r don't contain class name %r" % (
                    method_qualified_name, start_class_name))
                continue

            new_method_qualified_name = method_qualified_name.replace(start_class_name, end_class_name)

            parent_method_node_json = self.graph_data.find_one_node_by_property(
                property_name=GraphData.DEFAULT_KEY_PROPERTY_QUALIFIED_NAME,
                property_value=new_method_qualified_name)

            if not parent_method_node_json:
                continue

            override_pair = (method_node_id, parent_method_node_json[GraphData.DEFAULT_KEY_NODE_ID])
            override_method_pairs.append(override_pair)
            print("found %r override %r" % (method_qualified_name, new_method_qualified_name))
        return override_method_pairs

    def build_override_relation(self):
        print("start build override relation")
        print(self.graph_data)
        self.graph_data.print_graph_info()

        VALID_LABELS = {
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_CLASS),
            CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_INTERFACE),
        }

        extends_relation_str = CodeEntityRelationCategory.to_str(
            CodeEntityRelationCategory.RELATION_CATEGORY_EXTENDS)
        implement_relation_str = CodeEntityRelationCategory.to_str(
            CodeEntityRelationCategory.RELATION_CATEGORY_IMPLEMENTS)
        extend_relation_list = self.graph_data.get_relations(relation_type=extends_relation_str)
        implement_relation_list = self.graph_data.get_relations(relation_type=implement_relation_str)

        all_relation_list = set(extend_relation_list).union(set(implement_relation_list))
        for (start_class_id, relation_type, end_class_id) in all_relation_list:
            print("try to find extends relation for %r %r %r" % (start_class_id, relation_type, end_class_id))
            override_method_pairs = self.get_override_method_pairs(start_class_id, end_class_id)

            for start_method_id, end_method_id in override_method_pairs:
                self.graph_data.add_relation(start_method_id,
                                             CodeEntityRelationCategory.to_str(
                                                 CodeEntityRelationCategory.RELATION_CATEGORY_METHOD_OVERRIDING),
                                             end_method_id)

        print(self.graph_data)
        self.graph_data.print_graph_info()
        print("end build override relation")

    def build_aliases_for_code_element(self):
        name_util = CodeElementNameUtil()
        all_node_id_set = self.graph_data.get_node_ids()

        for node_id in all_node_id_set:
            node_json = self.graph_data.get_node_info_dict(node_id=node_id)
            if "simple_qualified_name" not in node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]:
                continue
            simple_qualified_name = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["simple_qualified_name"]

            labels = node_json[GraphData.DEFAULT_KEY_NODE_LABELS]

            include_parent_name = False
            if (CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD) in labels and CodeEntityCategory.to_str(
                    CodeEntityCategory.CATEGORY_CONSTRUCT_METHOD) not in labels) or CodeEntityCategory.to_str(
                CodeEntityCategory.CATEGORY_ENUM_CONSTANTS) in labels or CodeEntityCategory.to_str(
                CodeEntityCategory.CATEGORY_FIELD_OF_CLASS) in labels or CodeEntityCategory.to_str(
                CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD) in labels:
                include_parent_name = True

            name_list = name_util.generate_aliases(qualified_name=simple_qualified_name,
                                                   include_simple_parent_name=include_parent_name)

            if "simple_name" in node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]:
                name_list.append(node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["simple_name"])

            node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]["alias"] = list(set(name_list))

        self.graph_data.refresh_indexer()

    def add_source_label(self, label):
        print("adding the source label %r to nodes in graph" % label)
        self.graph_data.add_label_to_all(label)

    def build(self):
        """
        get the graph after builder
        :return: the graph data build successfully
        """
        return self.graph_data

    @catch_exception
    def build_use_jdk_constant_field_relation_from_code_doc(self, document_collection: MultiFieldDocumentCollection):
        if document_collection == None:
            raise Exception("The code document collection can't be None")

        constant_nodes = []
        for node_id in self.graph_data.get_node_ids_by_label(
                CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_FIELD_OF_CLASS)):
            node_json = self.graph_data.get_node_info_dict(node_id=node_id)
            if not node_json:
                continue
            node_properties = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]
            simple_constant_name = node_properties["qualified_name"].split(".")[-1]

            if len(node_properties["qualified_name"].split(".")) <= 2:
                continue
            parent_class_name = node_properties["qualified_name"].split(".")[-2]
            constant_nodes.append((node_id, parent_class_name + "." + simple_constant_name))
        # for t in constant_nodes:
        #     print(t)

        for node_id in self.graph_data.get_node_ids_by_label(
                CodeEntityCategory.to_str(CodeEntityCategory.CATEGORY_METHOD)):
            doc: MultiFieldDocument = document_collection.get_by_id(node_id)
            if doc == None:
                continue
            code_text = doc.get_doc_text_by_field("code")

            for constant_node_id, constant_node_name in constant_nodes:

                if constant_node_name not in code_text:
                    continue

                self.graph_data.add_relation(startId=node_id, endId=constant_node_id,
                                             relationType=CodeEntityRelationCategory.to_str(
                                                 CodeEntityRelationCategory.RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL_FIELD
                                             ))

        return self.graph_data

    def export_code_document_collection(self, code_doc_collection_path=None):
        """
        export a document collection containing all code
        :param code_doc_collection_path:
        :return:
        """
        collection = MultiFieldDocumentCollection()

        for node_id in self.graph_data.get_node_ids():
            node_json = self.graph_data.get_node_info_dict(node_id=node_id)

            properties = node_json[GraphData.DEFAULT_KEY_NODE_PROPERTIES]
            ## the code is empty is acceptable

            code = properties.get("code", None)
            if code != None:
                name = properties.get("qualified_name", "")
                if name == "":
                    continue

                doc = MultiFieldDocument(id=node_id, name=name)
                doc.add_field("code", code)
                doc.add_field("qualified_name", name)

                collection.add_document(document=doc)
        if code_doc_collection_path != None:
            collection.save(code_doc_collection_path)
        return collection
