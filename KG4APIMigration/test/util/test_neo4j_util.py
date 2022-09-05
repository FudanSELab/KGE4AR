from unittest import TestCase

from migration.util.db_util import DBUtil


class TestNeo4jUtil(TestCase):
    neo4j_util = DBUtil.get_test_api_kg_util()

    def test_get_library_id_by_node_id(self):
        pass

    def test_get_node_by_id(self):
        pass

    def test_get_node_by_qualified_name(self):
        test_case_list = ["com.google.gson.JsonArray.size()",
                          "org.apache.commons.io.IOUtils.readLines(java.io.InputStream)",
                          "org.apache.commons.httpclient.HttpMethodBase.getURI()",
                          "org.json.simple.JSONObject.toJSONString()",
                          "org.json.JSONArray",
                          "org.apache.commons.io.IOUtils",
                          "org.apache.commons.httpclient.HttpMethodBase",
                          "org.json.simple.JSONObject",
                          "org.json.JSONObject.getLong(java.lang.String)",
                          "org.json.JSONObject",
                          ]
        for test_name in test_case_list:
            node = self.neo4j_util.get_node_by_qualified_name(test_name)
            print(test_name, node["id"])
            print(node)

    def test_get_out_relation_node_by_qualified_name(self):
        test_case_list = ["com.google.gson.JsonArray.size()",
                          "org.apache.commons.io.IOUtils.readLines(java.io.InputStream)",
                          "org.apache.commons.httpclient.HttpMethodBase.getURI()",
                          "org.apache.commons.httpclient.URI.getURI()",
                          "org.apache.http.client.methods.HttpUriRequest.getURI()",
                          "org.apache.commons.httpclient.URI",
                          "org.apache.commons.httpclient.HttpMethodBase",
                          "org.apache.http.client.methods.HttpUriRequest",
                          "org.json.simple.JSONObject.toJSONString()",
                          "org.json.JSONArray",
                          "com.google.gson.JsonArray",
                          "org.apache.commons.io.IOUtils",
                          "org.apache.commons.httpclient.HttpMethodBase",
                          "org.json.simple.JSONObject",
                          "org.mockito.Mockito.mock(java.lang.Class)"]
        for test_name in test_case_list:
            node = self.neo4j_util.get_node_by_qualified_name(test_name)
            if not node:
                print("not found for ", test_name)
                continue
            print(test_name, node["id"])
            print(node)
            result = self.neo4j_util.get_out_relation_node(node["id"])
            for t in result:
                print(t)
            print("-" * 50)
