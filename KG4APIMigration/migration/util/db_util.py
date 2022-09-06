from milvus import Milvus
from py2neo import Graph

from definitions import RemoteMilvus, LargeNEO4J, TestNEO4J
from migration.util.milvus_util import MilvusUtil
from migration.util.neo4j_util import Neo4jUtil


class DBUtil:

    __large_api_kg_neo4j_graph = None
    __milvus = None
    __test_api_kg_neo4j_graph = None
    __milvus_util = None
    __large_api_kg_neo4j_graph_util = None
    __test_api_kg_neo4j_graph_util = None

    @classmethod
    def get_large_api_kg(cls) -> Graph:
        if cls.__large_api_kg_neo4j_graph is None:
            cls.__large_api_kg_neo4j_graph: Graph = Graph(LargeNEO4J.URI, user=LargeNEO4J.USERNAME,
                                                          password=LargeNEO4J.PASSWORD)
        return cls.__large_api_kg_neo4j_graph

    @classmethod
    def get_test_api_kg(cls) -> Graph:
        if cls.__test_api_kg_neo4j_graph is None:
            cls.__test_api_kg_neo4j_graph: Graph = Graph(TestNEO4J.URI, user=TestNEO4J.USERNAME,
                                                         password=TestNEO4J.PASSWORD)
        return cls.__test_api_kg_neo4j_graph

    @classmethod
    def get_milvus(cls) -> Milvus:
        """

        :rtype: object
        """
        if cls.__milvus is None:
            cls.__milvus: Milvus = Milvus(host=RemoteMilvus.HOST, port=RemoteMilvus.PORT)
        return cls.__milvus

    @classmethod
    def get_milvus_util(cls) -> MilvusUtil:
        if cls.__milvus_util is None:
            cls.__milvus_util: MilvusUtil = MilvusUtil(cls.get_milvus())
        return cls.__milvus_util

    @classmethod
    def get_large_api_kg_util(cls) -> Neo4jUtil:
        if cls.__large_api_kg_neo4j_graph_util is None:
            cls.__large_api_kg_neo4j_graph_util: Neo4jUtil = Neo4jUtil(cls.get_large_api_kg())
        return cls.__large_api_kg_neo4j_graph_util

    @classmethod
    def get_test_api_kg_util(cls) -> Neo4jUtil:
        if cls.__test_api_kg_neo4j_graph_util is None:
            cls.__test_api_kg_neo4j_graph_util: Neo4jUtil = Neo4jUtil(cls.get_test_api_kg())
        return cls.__test_api_kg_neo4j_graph_util
