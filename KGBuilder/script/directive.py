class DirectiveEntityCategory:
    """
    定义不同的约束节点的类型以及相关的标签
    """
    CATEGORY_DIRECTIVE_FORMULA_TREE = 29
    CATEGORY_DIRECTIVE_ATOMIC_FORMULA_TREE = 30

    CATEGORY_UNKNOWN = 31
    CATEGORY_VALUE = 32
    CATEGORY_RETURN_VALUE = 33
    CATEGORY_TYPE = 34
    CATEGORY_RETURN_TYPE = 35
    CATEGORY_THROWN_EXCEPTION = 36
    CATEGORY_METHOD_OVERRIDE = 37
    CATEGORY_DEPRECATED = 38
    CATEGORY_SAME_USAGE = 39

    category_code_to_str_map = {
        CATEGORY_UNKNOWN: "unknown directive",
        CATEGORY_VALUE: "value directive",
        CATEGORY_RETURN_VALUE: "return value directive",
        CATEGORY_TYPE: "type directive",
        CATEGORY_RETURN_TYPE: "return type directive",
        CATEGORY_THROWN_EXCEPTION: "thrown exception directive",
        CATEGORY_METHOD_OVERRIDE: "method override directive",
        CATEGORY_DEPRECATED: "deprecated directive",
        CATEGORY_SAME_USAGE: "same usage directive"
    }

    category_code_to_str_list_map = {
        CATEGORY_UNKNOWN: ["unknown directive"],
        CATEGORY_VALUE: ["value directive"],
        CATEGORY_RETURN_VALUE: ["value directive", "return value directive"],
        CATEGORY_TYPE: ["type directive"],
        CATEGORY_RETURN_TYPE: ["type directive", "return type directive"],
        CATEGORY_THROWN_EXCEPTION: ["thrown exception directive"],
        CATEGORY_METHOD_OVERRIDE: ["method override directive"],
        CATEGORY_DEPRECATED: ["deprecated directive"],
        CATEGORY_SAME_USAGE: ["same usage directive"]
    }

    @classmethod
    def to_str(cls, category_code):
        if category_code in cls.category_code_to_str_map:
            return cls.category_code_to_str_map[category_code]
        return "unknown directive"

    @classmethod
    def to_str_list(cls, category_code):
        if category_code in cls.category_code_to_str_list_map:
            return cls.category_code_to_str_list_map[category_code]
        return ["unknown directive"]

    @classmethod
    def directive_type_set(cls):
        return cls.category_code_to_str_map.keys()


class DirectiveRelationCategory:
    """
    定义在约束图之中，约束关系与不同API节点之间的关系
    """

    RELATION_CATEGORY_DIRECTIVE_BELONG_TO = 20
    RELATION_CATEGORY_DIRECTIVE_RELATED_TO = 21
    RELATION_CATEGORY_DIRECTIVE_EXTRACT_FROM = 22

    RELATION_CATEGORY_HAS_FORMULA_TREE = 23
    RELATION_CATEGORY_HAS_ATOMIC_FORMULA_TREE = 24

    category_code_to_str_map = {
        RELATION_CATEGORY_DIRECTIVE_BELONG_TO: "directive belong to",
        RELATION_CATEGORY_DIRECTIVE_RELATED_TO: "directive related to",
        RELATION_CATEGORY_DIRECTIVE_EXTRACT_FROM: " directive extract from",
        RELATION_CATEGORY_HAS_FORMULA_TREE: "has directive",
        RELATION_CATEGORY_HAS_ATOMIC_FORMULA_TREE: "has atomic directive"
    }

    @classmethod
    def to_str(cls, category_code):
        if category_code in cls.category_code_to_str_map:
            return cls.category_code_to_str_map[category_code]
        return "unknown"

    @classmethod
    def relation_set(cls):
        return cls.category_code_to_str_map.keys()
