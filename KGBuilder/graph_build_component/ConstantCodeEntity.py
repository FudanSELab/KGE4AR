class CodeEntityCategory:
    """
    the basic code type constant, define all things in code we care.
    can be used in model definition and other thing.
    Here we think there are three different category CodeEntity (Container,Type,Value).
    and sometimes one codeEntity could be Container and Type at the same time.

    When possible, you should use the most accurate categories, but in some cases, it is difficult to do so,
    You can use the most suitable type.

    For example, you don't know if an API Entity is an interface, then you can temporarily use TYPE_CLASS as his category,
    and change later.

    Explanation:

    1. Container, the CodeEntity could contain other CodeEntity
        - CATEGORY_PACKAGE, stand for the package, it could contain other class, interface.
        - CATEGORY_CLASS, stand for the class, it could contain method, field.
        - CATEGORY_INTERFACE, stand for the interface, it could contain method.
        - CATEGORY_EXCEPTION_CLASS, stand for the special class- Exception, the Exception class will thrown by method.
            actually TYPE_EXCEPTION_CLASS is subclass of TYPE_EXCEPTION_CLASS.
        - CATEGORY_ERROR_CLASS,  stand for the special class- Error, the Error class will thrown by method.
            actually TYPE_ERROR_CLASS is subclass of TYPE_EXCEPTION_CLASS.
        - CATEGORY_ENUM_CLASS, stand for the special class- ENUM,
        - CATEGORY_ANNOTATION_CLASS, stand for the special class- Annotation class, implement the annotation,

    2. Value, the CodeEntity stand for some value(instance) that has type and special meaning. type is necessary.

        For example, "name:Sting path; type:java.lang.String; description:the path to the file" is a parameter meaning the file path.
        - TYPE_RETURN_VALUE, meaning the return value instance of some methods. Only has the (type,description). and the description sometimes maybe empty.
        - CATEGORY_PARAMETER, meaning the parameter of the method. with type and
        - CATEGORY_FIELD, some field in class or interface, maybe constant or property of class.
            For example, java.awt.Color.RED, (type,name,description,value).
        - CATEGORY_EXCEPTION_CONDITION, description what and when the exception thrown.
        (exception type,description). For example, (type:NullPointerException, thrown when the parameter file path is Null)
        PS: it is not the exception class, it is the exception instance thrown by the method.
        - CATEGORY_LOCAL_VARIABLE, it stands for the local variable in method implement code.

    3. Type:
        - CATEGORY_PRIMARY_TYPE, the primary type for java, etc. int, long, short.
        - CATEGORY_CLASS, stand for the class, it could contain method, field.
        - CATEGORY_INTERFACE, stand for the interface, it could contain method.
        - CATEGORY_EXCEPTION_CLASS, stand for the special class- Exception, the Exception class will thrown by method.
            actually CATEGORY_EXCEPTION_CLASS is subclass of CATEGORY_EXCEPTION_CLASS.
        - CATEGORY_ERROR_CLASS,  stand for the special class- Error, the Error class will thrown by method.
            actually CATEGORY_ERROR_CLASS is subclass of CATEGORY_EXCEPTION_CLASS.
        - CATEGORY_ENUM_CLASS, stand for the special class- ENUM,

    3. Other,
        - CATEGORY_METHOD, the all method, actually the CATEGORY_CONSTRUCT_METHOD is also count for method.
        - CATEGORY_CONSTRUCT_METHOD, special method but also belong to method.
        - CATEGORY_ANNOTATION, some annotation in java. Etc."@Nullable"
        - CATEGORY_XML_ATTRIBUTE, some xml attribute, normally for android. But we think it is not so useful. Maybe we should delete it.
        - CATEGORY_ENUM_CONSTANTS, the constant in CATEGORY_ENUM_CLASS,

        - CATEGORY_BASE_OVERRIDE_METHOD, the parent node for all overriding method without parameters.
        etc. java.util.List.add, java.util.List.append
        - CATEGORY_METHOD_CALL_INSTANCE: the instance for a method call with parameter.
        For example, java.util.List.append(1),java.util.List.append(a)
        - CATEGORY_VALUE, the base type for CATEGORY_PARAMETER,CATEGORY_FIELD,TYPE_RETURN_VALUE
        - CATEGORY_CLASS_FIELD, some special field value, eg.java.awt.AlphaComposite.SrcAtop, java.awt.Color.BLACK.
        Because the extraction, we may not know the value's type, but we has its qualified name and which class that it belong to.

    """
    CATEGORY_UNKNOWN = 0
    CATEGORY_PACKAGE = 1
    CATEGORY_CLASS = 2
    CATEGORY_INTERFACE = 3
    CATEGORY_EXCEPTION_CLASS = 4
    CATEGORY_ERROR_CLASS = 5
    CATEGORY_FIELD = 6
    CATEGORY_CONSTRUCT_METHOD = 7
    CATEGORY_ENUM_CLASS = 8
    CATEGORY_ANNOTATION_CLASS = 9
    CATEGORY_XML_ATTRIBUTE = 10
    CATEGORY_METHOD = 11
    CATEGORY_ENUM_CONSTANTS = 12
    CATEGORY_PRIMARY_TYPE = 13
    CATEGORY_PARAMETER = 14
    CATEGORY_RETURN_VALUE = 15
    CATEGORY_EXCEPTION_CONDITION = 16
    CATEGORY_BASE_OVERRIDE_METHOD = 17
    CATEGORY_VALUE = 18
    CATEGORY_FIELD_OF_CLASS = 19
    CATEGORY_LOCAL_VARIABLE = 20
    CATEGORY_PROPERTY = 21
    CATEGORY_ATTACHED_PROPERTY = 22
    CATEGORY_OPERATOR = 23
    CATEGORY_EVENT = 24
    CATEGORY_STRUCT = 25
    CATEGORY_ATTACHED_EVENT = 26
    CATEGORY_DELEGATE = 27
    CATEGORY_CONSTRUCTORS = 28
    CATEGORY_EXCEPTION_CODE_DIRECTIVE = 29
    CATEGORY_RETURN_CODE_DIRECTIVE = 30

    category_code_to_str_map = {
        CATEGORY_UNKNOWN: "unknown",
        CATEGORY_PACKAGE: "package",
        CATEGORY_CLASS: "class",
        CATEGORY_INTERFACE: "interface",
        CATEGORY_EXCEPTION_CLASS: "exception class",
        CATEGORY_ERROR_CLASS: "error class",
        CATEGORY_RETURN_VALUE: "return value",
        CATEGORY_CONSTRUCT_METHOD: "construct method",
        CATEGORY_ENUM_CLASS: "enum class",
        CATEGORY_ANNOTATION_CLASS: "annotation class",
        CATEGORY_XML_ATTRIBUTE: "xml attribute",
        CATEGORY_METHOD: "method",
        CATEGORY_ENUM_CONSTANTS: "enum constants",
        CATEGORY_PRIMARY_TYPE: "primary type",
        CATEGORY_PARAMETER: "parameter",
        CATEGORY_FIELD: "field",
        CATEGORY_EXCEPTION_CONDITION: "exception condition",
        CATEGORY_BASE_OVERRIDE_METHOD: "base override method",
        CATEGORY_VALUE: "value",
        CATEGORY_FIELD_OF_CLASS: "field of class",
        CATEGORY_LOCAL_VARIABLE: "local variable",
        CATEGORY_PROPERTY: "property",
        CATEGORY_ATTACHED_PROPERTY: "attached property",
        CATEGORY_OPERATOR: "operator",
        CATEGORY_EVENT: "event",
        CATEGORY_STRUCT: "struct",
        CATEGORY_ATTACHED_EVENT: "attached event",
        CATEGORY_DELEGATE: "delegate",
        CATEGORY_CONSTRUCTORS: "constructors",
        CATEGORY_EXCEPTION_CODE_DIRECTIVE: "exception code directive",
        CATEGORY_RETURN_CODE_DIRECTIVE: "return code directive"
    }

    category_code_to_str_list_map = {
        CATEGORY_UNKNOWN: ["unknown"],
        CATEGORY_PACKAGE: ["package"],
        CATEGORY_CLASS: ["class", "type"],
        CATEGORY_INTERFACE: ["interface", "type"],
        CATEGORY_EXCEPTION_CLASS: ["exception class", "class", "type"],
        CATEGORY_ERROR_CLASS: ["error class", "class", "type"],
        CATEGORY_RETURN_VALUE: ["return value", "value"],
        CATEGORY_CONSTRUCT_METHOD: ["construct method", "method"],
        CATEGORY_ENUM_CLASS: ["enum class", "class", "type"],
        CATEGORY_ANNOTATION_CLASS: ["annotation class", "class"],
        CATEGORY_XML_ATTRIBUTE: ["xml attribute"],
        CATEGORY_METHOD: ["method"],
        CATEGORY_ENUM_CONSTANTS: ["enum constants"],
        CATEGORY_PRIMARY_TYPE: ["primary type", "type"],
        CATEGORY_PARAMETER: ["parameter", "value"],
        CATEGORY_FIELD: ["field", "value"],
        CATEGORY_EXCEPTION_CONDITION: ["exception condition", "value"],
        CATEGORY_BASE_OVERRIDE_METHOD: ["base override method"],
        CATEGORY_VALUE: ["value"],
        CATEGORY_FIELD_OF_CLASS: ["field of class"],
        CATEGORY_LOCAL_VARIABLE: ["local variable", "value"],
        CATEGORY_PROPERTY: ["property"],
        CATEGORY_ATTACHED_PROPERTY: ["attached property"],
        CATEGORY_OPERATOR: ["operator"],
        CATEGORY_EVENT: ["event"],
        CATEGORY_STRUCT: ["struct"],
        CATEGORY_ATTACHED_EVENT: ["attached event"],
        CATEGORY_DELEGATE: ["delegate"],
        CATEGORY_CONSTRUCTORS: ["constructors"],
        CATEGORY_EXCEPTION_CODE_DIRECTIVE: ["exception code directive", "value"],
        CATEGORY_RETURN_CODE_DIRECTIVE: ["return code directive", "value"]
    }

    JAVA_PRIMARY_TYPE_BYTE = "byte"
    JAVA_PRIMARY_TYPE_CHAR = "char"
    JAVA_PRIMARY_TYPE_SHORT = "short"
    JAVA_PRIMARY_TYPE_INT = "int"
    JAVA_PRIMARY_TYPE_LONG = "long"
    JAVA_PRIMARY_TYPE_FLOAT = "float"
    JAVA_PRIMARY_TYPE_DOUBLE = "double"
    JAVA_PRIMARY_TYPE_BOOLEAN = "boolean"
    JAVA_PRIMARY_TYPE_VOID = "void"

    NET_PRIMARY_TYPE_BYTE = "byte"
    NET_PRIMARY_TYPE_CHAR = "char"
    NET_PRIMARY_TYPE_SHORT = "short"
    NET_PRIMARY_TYPE_USHORT = "ushort"
    NET_PRIMARY_TYPE_DECIMAL = "decimal"
    NET_PRIMARY_TYPE_INT = "int"
    NET_PRIMARY_TYPE_UINT = "uint"
    NET_PRIMARY_TYPE_LONG = "long"
    NET_PRIMARY_TYPE_ULONG = "ulong"
    NET_PRIMARY_TYPE_FLOAT = "float"
    NET_PRIMARY_TYPE_DOUBLE = "double"
    NET_PRIMARY_TYPE_BOOL = "bool"
    NET_PRIMARY_TYPE_SBYTE = "sbyte"
    NET_PRIMARY_TYPE_VOID = "void"

    JAVA_PRIMARY_TYPES = [
        {
            "name": "byte",
            "description": "byte is a keyword which designates the 8 bit signed integer primitive type. The java.lang.Byte class is the nominal wrapper class when you need to store a byte value but an object reference is required."},
        {
            "name": "char",
            "description": "char is a keyword. It defines a character primitive type. char can be created from character literals and numeric representation. Character literals consist of a single quote character (') (ASCII 39, hex 0x27), a single character, and a close quote ('), such as 'w'. Instead of a character, you can also use unicode escape sequences, but there must be exactly one."},
        {
            "name": "short",
            "description": "short is a keyword. It defines a 16 bit signed integer primitive type."},
        {
            "name": "int",
            "description": "int is a keyword which designates the 32 bit signed integer primitive type. The java.lang.Integer class is the nominal wrapper class when you need to store an int value but an object reference is required."
        },
        {
            "name": "long",
            "description": "long is a keyword which designates the 64 bit signed integer primitive type. The java.lang.Long class is the nominal wrapper class when you need to store a long value but an object reference is required."},
        {
            "name": "float",
            "description": "float is a keyword which designates the 32 bit float primitive type. The java.lang.Float class is the nominal wrapper class when you need to store a float value but an object reference is required."},
        {
            "name": "double",
            "description": "double is a keyword which designates the 64 bit float primitive type. The java.lang.Double class is the nominal wrapper class when you need to store a double value but an object reference is required."},
        {
            "name": "boolean",
            "description": "boolean is a keyword which designates the boolean primitive type. There are only two possible boolean values: true and false. The default value for boolean fields is false."},

        {
            "name": "void",
            "description": "void is a Java keyword. Used at method declaration and definition to specify that the method does not return any type, the method returns void. It is not a type and there is no void references/pointers as in C/C++."},
    ]
    NET_PRIMARY_TYPES = [
        {
            "name": "byte",
            "description": "byte is a keyword which designates the 8 bit signed integer primitive type. The java.lang.Byte class is the nominal wrapper class when you need to store a byte value but an object reference is required."},
        {
            "name": "char",
            "description": "char is a keyword. It defines a character primitive type. char can be created from character literals and numeric representation. Character literals consist of a single quote character (') (ASCII 39, hex 0x27), a single character, and a close quote ('), such as 'w'. Instead of a character, you can also use unicode escape sequences, but there must be exactly one."},
        {
            "name": "short",
            "description": "short is a keyword. It defines a 16 bit signed integer primitive type."},
        {
            "name": "int",
            "description": "int is a keyword which designates the 32 bit signed integer primitive type. The java.lang.Integer class is the nominal wrapper class when you need to store an int value but an object reference is required."
        },
        {
            "name": "long",
            "description": "long is a keyword which designates the 64 bit signed integer primitive type. The java.lang.Long class is the nominal wrapper class when you need to store a long value but an object reference is required."},
        {
            "name": "float",
            "description": "float is a keyword which designates the 32 bit float primitive type. The java.lang.Float class is the nominal wrapper class when you need to store a float value but an object reference is required."},
        {
            "name": "double",
            "description": "double is a keyword which designates the 64 bit float primitive type. The java.lang.Double class is the nominal wrapper class when you need to store a double value but an object reference is required."},
        {
            "name": "bool",
            "description": "bool is a keyword which designates the boolean primitive type. There are only two possible boolean values: true and false. The default value for boolean fields is false."},
        {
            "name": "void",
            "description": "void is a Java keyword. Used at method declaration and definition to specify that the method does not return any type, the method returns void. It is not a type and there is no void references/pointers as in C/C++."},
        {
            "name": "ushort",
            "description": "Use the UShort data type to contain binary data too large for Byte. The default value of UShort is 0."},
        {
            "name": "decimal",
            "description": "Holds signed 128-bit (16-byte) values representing 96-bit (12-byte) integer numbers scaled by a variable power of 10. The scaling factor specifies the number of digits to the right of the decimal point; it ranges from 0 through 28."},
        {
            "name": "uint",
            "description": "0 to 4,294,967,295	Unsigned 32-bit integer	System.UInt32"
        },
        {
            "name": "ulong",
            "description": "0 to 18,446,744,073,709,551,615	Unsigned 64-bit integer	System.UInt64"
        },
        {
            "name": "sbyte",
            "description": "Represents a signed 8-bit integer with values ​​ranging from -128 to 127"
        },
    ]
    JAVA_PRIMARY_TYPE_SET = {
        JAVA_PRIMARY_TYPE_BYTE,
        JAVA_PRIMARY_TYPE_CHAR,
        JAVA_PRIMARY_TYPE_SHORT,
        JAVA_PRIMARY_TYPE_INT,
        JAVA_PRIMARY_TYPE_LONG,
        JAVA_PRIMARY_TYPE_FLOAT,
        JAVA_PRIMARY_TYPE_DOUBLE,
        JAVA_PRIMARY_TYPE_BOOLEAN,
        JAVA_PRIMARY_TYPE_VOID,
    }
    NET_PRIMARY_TYPE_SET = {
        NET_PRIMARY_TYPE_BYTE,
        NET_PRIMARY_TYPE_CHAR,
        NET_PRIMARY_TYPE_SHORT,
        NET_PRIMARY_TYPE_USHORT,
        NET_PRIMARY_TYPE_DECIMAL,
        NET_PRIMARY_TYPE_INT,
        NET_PRIMARY_TYPE_LONG,
        NET_PRIMARY_TYPE_ULONG,
        NET_PRIMARY_TYPE_FLOAT,
        NET_PRIMARY_TYPE_DOUBLE,
        NET_PRIMARY_TYPE_BOOL,
        NET_PRIMARY_TYPE_SBYTE,
        NET_PRIMARY_TYPE_UINT,
        NET_PRIMARY_TYPE_VOID,
    }

    @staticmethod
    def java_primary_types():
        return CodeEntityCategory.JAVA_PRIMARY_TYPES

    @staticmethod
    def net_primary_types():
        return CodeEntityCategory.NET_PRIMARY_TYPES

    @staticmethod
    def to_str(category_code):
        if category_code in CodeEntityCategory.category_code_to_str_map:
            return CodeEntityCategory.category_code_to_str_map[category_code]
        return "unknown"

    @staticmethod
    def to_str_list(category_code):
        if category_code in CodeEntityCategory.category_code_to_str_list_map:
            return CodeEntityCategory.category_code_to_str_list_map[category_code]
        return ["unknown"]

    @staticmethod
    def is_basic_type(type_str):
        if type_str in CodeEntityCategory.JAVA_PRIMARY_TYPE_SET:
            return True
        return False

    @staticmethod
    def entity_type_set():
        return CodeEntityCategory.category_code_to_str_map.keys()


class CodeEntityRelationCategory:
    """
    describe different relation between CodeEntity

    - RELATION_CATEGORY_BELONG_TO, the belong to relation between CodeEntity,
         (Method, belongTo, Class/Interface), (Class/Interface, belongTo, Package),
    - RELATION_CATEGORY_EXTENDS, the extends relation between class.
        (Class, extends, Class)
    - RELATION_CATEGORY_IMPLEMENTS, the implement relation between class and interface.
        (Class,implements, Interface)
    - RELATION_CATEGORY_SEE_ALSO, the see also relation between CodeEntity
        eg. (Method, seeAlso, Method)
    - RELATION_CATEGORY_THROW_EXCEPTION_TYPE, between the Exception class and the Method
        (Method, THROW_EXCEPTION_TYPE, Exception class). eg. (java.io.File,THROW_EXCEPTION_TYPE,java.lang.FileNotExistException)
    - RELATION_CATEGORY_RETURN_VALUE_TYPE, between the Class and the Method
        (Method, RETURN_VALUE_TYPE, Exception class). eg. (java.applet.AppletContext.getApplet(java.lang.String),java.applet.Applet)

    - RELATION_CATEGORY_HAS_PARAMETER, between the Method and Parameter value entity,
    - RELATION_CATEGORY_HAS_RETURN_VALUE, between the Method and Return  Value entity,
    - RELATION_CATEGORY_HAS_EXCEPTION_CONDITION, between the Method and EXCEPTION_CONDITION
    - RELATION_CATEGORY_HAS_FIELD, between the Class and field
    - RELATION_CATEGORY_HAS_TYPE, between the Value-CodeEntity and its Type.
    - RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL, some method are call other Method



    - RELATION_CATEGORY_METHOD_OVERRIDING, same method with same parameters in different extended classes
    - RELATION_CATEGORY_METHOD_OVERLOADING, same method with different method parameter in a class
    - RELATION_CATEGORY_METHOD_INSTANCE_CALL, the instance call between method instance and method
    - RELATION_CATEGORY_USE_LOCAL_VARIABLE, the implement code of some method use some local variable. the local variable has name and type.
    """
    RELATION_CATEGORY_BELONG_TO = 1
    RELATION_CATEGORY_EXTENDS = 2
    RELATION_CATEGORY_IMPLEMENTS = 3
    RELATION_CATEGORY_SEE_ALSO = 4

    # relation between method and type
    RELATION_CATEGORY_THROW_EXCEPTION_TYPE = 5
    RELATION_CATEGORY_RETURN_VALUE_TYPE = 6

    # relation between method and the Value-category entity
    RELATION_CATEGORY_HAS_PARAMETER = 7
    RELATION_CATEGORY_HAS_RETURN_VALUE = 8
    RELATION_CATEGORY_HAS_EXCEPTION_CONDITION = 9

    # relation for class and field
    RELATION_CATEGORY_HAS_FIELD = 10
    RELATION_CATEGORY_TYPE_OF = 11
    RELATION_CATEGORY_FIELD_OF = 12

    RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL_METHOD = 13
    RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_USE_CLASS = 14
    RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL_FIELD = 15

    RELATION_CATEGORY_METHOD_OVERRIDING = 16  # same method with same parameters in different extended classes
    RELATION_CATEGORY_METHOD_OVERLOADING = 17  # same method with different method parameter in a class

    RELATION_CATEGORY_SUBCLASS_OF = 18
    RELATION_CATEGORY_USE_LOCAL_VARIABLE = 19

    RELATION_CATEGORY_HAS_EXCEPTION_CODE_DIRECTIVE = 20
    RELATION_CATEGORY_HAS_RETURN_CODE_DIRECTIVE = 21

    RELATION_CATEGORY_HAS_CLASS = 22
    RELATION_CATEGORY_HAS_METHOD = 23

    category_code_to_str_map = {
        RELATION_CATEGORY_BELONG_TO: "belong to",
        RELATION_CATEGORY_EXTENDS: "extends",
        RELATION_CATEGORY_IMPLEMENTS: "implements",
        RELATION_CATEGORY_SEE_ALSO: "see also",
        RELATION_CATEGORY_THROW_EXCEPTION_TYPE: "thrown exception type",
        RELATION_CATEGORY_RETURN_VALUE_TYPE: "return value type",
        RELATION_CATEGORY_HAS_PARAMETER: "has parameter",
        RELATION_CATEGORY_HAS_RETURN_VALUE: "has return value",
        RELATION_CATEGORY_HAS_EXCEPTION_CONDITION: "has exception condition",
        RELATION_CATEGORY_HAS_FIELD: "has field",
        RELATION_CATEGORY_TYPE_OF: "type of",
        RELATION_CATEGORY_FIELD_OF: "field of",
        RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL_METHOD: "call method",
        RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_USE_CLASS: "use class",
        RELATION_CATEGORY_METHOD_IMPLEMENT_CODE_CALL_FIELD: "call field",

        RELATION_CATEGORY_METHOD_OVERRIDING: "overriding",
        RELATION_CATEGORY_METHOD_OVERLOADING: "overloading",

        RELATION_CATEGORY_SUBCLASS_OF: "subclass of",
        RELATION_CATEGORY_USE_LOCAL_VARIABLE: "use local variable",

        RELATION_CATEGORY_HAS_EXCEPTION_CODE_DIRECTIVE: "has exception code directive",
        RELATION_CATEGORY_HAS_RETURN_CODE_DIRECTIVE: "has return code directive",

        RELATION_CATEGORY_HAS_CLASS: "has class",
        RELATION_CATEGORY_HAS_METHOD: "has method"
    }

    @staticmethod
    def to_str(category_code):
        if category_code in CodeEntityRelationCategory.category_code_to_str_map:
            return CodeEntityRelationCategory.category_code_to_str_map[category_code]
        return "unknown"

    @staticmethod
    def relation_set():
        return CodeEntityRelationCategory.category_code_to_str_map.keys()
