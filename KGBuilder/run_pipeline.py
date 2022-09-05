# -*- coding: utf-8 -*-
import json
import logging

import zipfile
import subprocess
from pathlib import Path

import requests
from kgdt.neo4j.accessor.base import GraphAccessor
from kgdt.transfer.neo4j import Neo4jImporter

from definitions import *
from script.csv_import_neo4j import CSVImporter
from script.custom_log import LogUtil
from script.get_libraries_from_neo4j import Neo4jQuery
from script.graph_build import graph_build

from py2neo import Graph
from kgdt.models.graph import GraphData

# todo: 优化抽取代码
from script.import_timeout_check import ImportTimeoutCheck


class KGBuilder:
    # 指定结果保存路径
    def __init__(self):
        self.logger = LogUtil.get_log_util()

    def get_libraries_info(self, extract_max=None):
        self.logger.info("-------------Step 1: Start getting Library information---------")
        # 指定提取的语言类型，首字母要大写 e.g.Python
        language_type_list = ["Java", "Python"]
        # 指定提取的信息
        extract_info_key = ['repository ID', 'project name', 'repository URL', 'language',
                            'latest release publish timestamp']
        # 指定最大抽取数量
        if not extract_max:
            extract_max = 99999999999
        # 执行
        cypher = Neo4jQuery()
        cypher.get_libraries(language_type_list, extract_max, extract_info_key, save_path=PROJECT_DIR)
        for i in language_type_list:
            file_path = os.path.join(PROJECT_DIR, i) + ".json"
            # 添加日志信息
            with open(file_path, 'r') as fp:
                json_data = json.load(fp)
                self.logger.info("Got {} {} Libraries".format(len(json_data), i))
        self.logger.info("Get Library information finished.\n\n")

    # 指定从json文件中提取的语言类型(首字母要大写) 和提取数量，克隆仓库  ----已废弃
    # 使用需要安装GitPython库  from git import Repo
    def get_clone_repository(self, language_type, max_num=5):
        self.logger.info("Start cloning Library repositories")
        # 定义不同文件类型的仓库最终需要保留的文件格式
        language_type_to_keep_format = {'Java': ['.java'],
                                        'Python': ['.py']}
        # 拼接json路径
        file_path = os.path.join(PROJECT_DIR, language_type) + '.json'
        with open(file_path, 'r') as fp:
            json_data = json.load(fp)
            for i, node in enumerate(json_data):
                if i == max_num:
                    return
                url = node['repository URL'].replace('https://github.com', 'https://github.com.cnpmjs.org')

                path_with_name = os.path.join(REPOSITORIES_DIR, language_type, node['project name'])

                # 如果已经有了这个同名仓库，则跳过
                if os.path.exists(path_with_name):
                    self.logger.warning('Clone repository [{}] already existed, skipping!'.format(node['project name']))
                    continue

                try:
                    Repo.clone_from(url, path_with_name)
                    self.logger.info('Clone repository [{}] finished!'.format(node['project name']))

                    for file_format in language_type_to_keep_format['language_type']:
                        # 因为目前只解析java库，所以删除其他格式的文件，以节约空间
                        # 删除所有非java文件
                        for root, subdirectories, files in os.walk(path_with_name, topdown=False):
                            for file in files:
                                if not file.endswith(file_format):
                                    os.remove(os.path.join(root, file))
                        # 删除所有空目录
                        for root, subdirectories, files in os.walk(path_with_name, topdown=False):
                            if not subdirectories and not files:
                                os.rmdir(root)
                except:
                    self.logger.warning('Clone repository [{}] failed!'.format(node['project name']))

        self.logger.info("Clone repositories has been completed")

    def get_repo(self, language_type, max_num=None):
        self.logger.info("-------------Step 2: Start download Library repositories---------")

        # 判断路径是否存在
        if not os.path.exists(REPOSITORIES_DIR):
            os.mkdir(REPOSITORIES_DIR)
        java_repo_path = os.path.join(REPOSITORIES_DIR, language_type)
        if not os.path.exists(java_repo_path):
            os.mkdir(java_repo_path)

        # 拼接json路径,获取groupId和artifactId
        file_path = os.path.join(PROJECT_DIR, language_type) + '.json'
        with open(file_path, 'r') as fp:
            json_data = json.load(fp)
            if max_num:
                total = max_num
            else:
                total = len(json_data)
            successes_count = 0

            for i, node in enumerate(json_data):
                if max_num and i == max_num:
                    return
                self.logger.info("current library {} , {}/{}".format(node['project name'], i + 1, total))
                if self.download_and_filter_files_for_jar(java_repo_path, node['project name']):
                    successes_count += 1
                    self.logger.info(
                        "{} succeeded with number {} succeeded\n".format(node['project name'], successes_count))
            self.logger.info("Download repositories finished with {} succeeded\n\n".format(successes_count))

    # 通过库名下载jar包，解压后过滤掉java以外的文件格式
    def download_and_filter_files_for_jar(self, path, project_name):
        try:
            groupId = project_name.split(':')[0]
            # 部分project name不符合要求，如project name: "IsraelHiking.Elasticsearch",
            artifactId = project_name.split(':')[1]
        except IndexError:
            self.logger.warning('Project name is invalid')
            return False

        # 获取artifactId的最新版本信息
        url = "https://search.maven.org/solrsearch/select?q=g:{g}+AND+a:{a}&core=gav&rows=20&wt=json".format(
            g=groupId,
            a=artifactId)
        try:
            res = requests.get(url)
            json_data = res.json()
            v = json_data['response']['docs'][0]['v']
            self.logger.info('Get the latest version: {}'.format(v))

        except:
            self.logger.warning('Can not get version information from {}'.format(url))
            return False

        # 拼接下载路径，下载jar包
        url_prefix = 'https://search.maven.org/remotecontent?filepath='
        url_download = url_prefix + groupId.replace('.',
                                                    '/') + '/' + artifactId + '/' + v + '/' + artifactId + '-' + v + '-sources.jar'
        try:
            r = requests.get(url_download)
            filename = groupId + ':' + artifactId + '-version:' + v
            folder_name_with_path = os.path.join(path, filename)
            jar_name_with_path = os.path.join(path, filename) + '.jar'

            with open(jar_name_with_path, "wb") as code:
                code.write(r.content)
                code.close()
                self.logger.info('Download succeeded! ')

        except:
            self.logger.warning('Can not get jar from {}'.format(url_download))
            return False

        # 解压并过滤文件
        try:
            z = zipfile.ZipFile(jar_name_with_path, 'r')
            #  unpack the
            z.extractall(path=folder_name_with_path)

            self.logger.info('uncompress jar succeeded! ')
            #  通过后缀过滤（删除）掉所有.java后缀类型的文件
            self.file_filter_by_type(folder_name_with_path, '.java')
            self.del_old_zip(jar_name_with_path)
            self.logger.info('Processing finished')
            return True

        except:
            self.logger.warning('Can not uncompress jar for {}.jar'.format(filename))
            self.del_old_zip(jar_name_with_path)
            return False

    def file_filter_by_type(self, path, file_format):
        '''
        通过后缀过滤（删除）掉所有非指定类型的文件 如 .java
        '''
        for root, subdirectories, files in os.walk(path, topdown=False):
            for file in files:
                if not file.endswith(file_format):
                    os.remove(os.path.join(root, file))
        # 删除所有空目录
        for root, subdirectories, files in os.walk(path, topdown=False):
            if not subdirectories and not files:
                os.rmdir(root)

    def del_old_zip(self, file_path):
        os.remove(file_path)

    def repository_parser(self, input_dir=JAVA_REPOSITORIES_DIR, output_dir=REPOSITORIES_PARSER_DIR):
        self.logger.info("-------------Step 3: Start parsing Library repositories---------")
        if not os.path.exists(input_dir):
            self.logger.error("input_dir {} is not existed".format(JAVA_REPOSITORIES_DIR))
            return

        # 获取项目仓库的一级目录
        file_list = [x[1] for x in os.walk(input_dir)][0]
        total = len(file_list)
        successes_count = 0

        # 进程队列，保持5个进程
        process_max = 2
        current_process_num = 0
        # 设置一个起始值
        start_repository_num = 0
        current_repository_num = start_repository_num + 0

        while current_process_num <= process_max:
            current_process_num += 1

            file_name = file_list[current_repository_num]
            # 获得目录完整路径
            file = os.path.join(input_dir, file_name)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            output_dir_new = os.path.join(output_dir, file_name)
            if not os.path.exists(output_dir_new):
                os.mkdir(output_dir_new)
            else:
                break
            self.logger.info('current repository [{}] with {}/{}'.format(file_name, current_repository_num + 1, total))
            # 配置运行jar包所需要的参数
            cmd = ['java', '-jar', JAR_PATH,
                   '-i', file,
                   '-o', output_dir_new]
            try:
                # 添加超时时间为600S
                subprocess.call(cmd, 600)
                successes_count += 1
                self.logger.info("parser {} succeeded with {} succeeded\n".format(file_name, successes_count))

            except:
                self.logger.warning("parser {} failed.\n".format(file_name))

            finally:
                current_process_num -= 1
                if current_repository_num < total - 1:
                    current_repository_num += 1
                else:
                    self.logger.info("Parser repositories finished with {} succeeded\n\n".format(successes_count))
                    return

    # 为解析出来的json文件添加全限定名（保证名字唯一）
    def add_library_name(self, repositories_parser_dir=REPOSITORIES_PARSER_DIR):
        file_list = [x[0] for x in os.walk(repositories_parser_dir)][1:]
        for i, path in enumerate(file_list):
            # 获取库名
            library_qualified_name = path[path.find(str(repositories_parser_dir)) + len(
                repositories_parser_dir) + 1:path.find("-version:")]
            # 版本号
            version = path[path.find("-version:") + len("-version:"):]

            json_list = [x[2] for x in os.walk(path)][0]

            for j in json_list:
                print(os.path.join(path, j))
                with open(os.path.join(path, j), 'r+') as file:

                    file_data = json.load(file)
                    for f in file_data:
                        print(f)
                        if f:
                            f["library_qualified_name"] = library_qualified_name
                            f["version"] = version
                    file.seek(0)
                    json.dump(file_data, file, indent=4)
                file.close()

    def graph_build(self, doc_source_path=REPOSITORIES_PARSER_DIR):
        self.logger.info("-------------Step 4: Start building Library graphdata---------")
        # 获取位置/库名/版本号
        file_list = [x[0] for x in os.walk(doc_source_path)][1:]
        total = len(file_list)
        successes_count = 0

        for i, file in enumerate(file_list):
            # 获取库名
            print(doc_source_path)
            library_name = file[file.find(str(doc_source_path)) + len(doc_source_path) + 1:file.find("-version:")]
            # 版本号
            version = file[file.find("-version:") + len("-version:"):]
            print(file, library_name, version)
            self.logger.info("current num: {}/{}".format(i + 1, total))

            try:
                graph_build(library_name, version, doc_source_path=file)
                successes_count += 1
                self.logger.info("graph build {} succeeded with {} succeeded".format(library_name, successes_count))
            except:
                self.logger.warning("graph build {} failed.\n".format(library_name))

        self.logger.info("Build graphdata finished with {} succeeded\n\n".format(successes_count))

    def neo4j_import(self, kg_path=KG_DIR):
        self.logger.info("-------------Step 5: Start importing neo4j from graphdata---------")
        # 连接数据库
        ip = ExportNeo4jConfigure.IP
        username = ExportNeo4jConfigure.USERNAME
        password = ExportNeo4jConfigure.PASSWORD
        graph = Graph(ip, auth=(username, password))
        graph_accessor = GraphAccessor(graph)
        importer = Neo4jImporter(graph_accessor)
        successes_count = 0

        # 获取资源
        file_list = [x[0] for x in os.walk(kg_path)][1:]

        for i, path in enumerate(file_list):
            sub_file_list = [x[2] for x in os.walk(path)][0]
            for j, sub_path in enumerate(sub_file_list):
                if sub_path.endswith('.graph'):
                    graph_data: GraphData = GraphData.load(os.path.join(path, sub_path))

                    try:
                        importer.import_all_graph_data(graph_data, clear=False)
                        successes_count += 1
                        self.logger.info("import {} success with {} succeeded".format(sub_path, successes_count))
                    except:
                        self.logger.warning("import {} failed".format(sub_path))

        self.logger.info("Import neo4j finished\n\n")

    def neo4j_import_batch(self, kg_path=KG_DIR):
        self.logger.info("-------------Step 5: Start importing neo4j from graphdata---------")

        # 连接数据库
        ip = ExportNeo4jConfigure.IP
        username = ExportNeo4jConfigure.USERNAME
        password = ExportNeo4jConfigure.PASSWORD
        graph = Graph(ip, auth=(username, password))
        graph_accessor = GraphAccessor(graph)
        successes_count = 0
        csv_importer = CSVImporter()
        # 存放临时文件csv的路径

        # 获取资源
        file_list = [x[0] for x in os.walk(kg_path)][1:]
        total = len(file_list)
        start_index = 0
        for index, path in enumerate(file_list):
            if index < start_index:
                continue
            self.logger.info("current num: {}/{}: {}".format(index + 1, total, path))
            sub_file_list = [x[2] for x in os.walk(path)][0]
            if len(sub_file_list) == 0:
                self.logger.warning("import failed due to folder is empty")
            for j, sub_path in enumerate(sub_file_list):
                if sub_path.endswith('.graph'):
                    graph_data: GraphData = GraphData.load(os.path.join(path, sub_path))
                    lib_name = Path(sub_path).stem
                    self.logger.info("current lib: {}".format(lib_name))
                    # try:
                    c = ImportTimeoutCheck(csv_importer, graph_accessor, graph_data, KG_CSV_DIR, lib_name, index)
                    # 设置导入超时时间为10分钟
                    c.join(600)
                    if c.is_alive():
                        self.logger.warning("import failed due to timeout")
                        continue
                    elif c.error:
                        self.logger.warning("import {} failed due to execute error".format(sub_path))
                        continue
                    successes_count += 1
                    self.logger.info("import success with {} succeeded".format(successes_count))
                    # except:
                    #     self.logger.warning("import failed due to execute neo4j_import_batch error")

        self.logger.info("Import neo4j finished\n\n")


if __name__ == "__main__":
    kg_builder = KGBuilder()
    #  step1: 从指定的neo4j服务中获取第三方库信息，并存为json文件（主要获取仓库名字和链接）
    # kg_builder.get_libraries_info(5)

    # step2: 指定从json文件中提取的语言类型(首字母要大写) 和提取数量，下载jar文件
    # kg_builder.get_repo('Java', 15)
    #
    # step3:  对下载的仓库源码解压并进行分析，生成json文件 对于无法解压的文件直接删除
    #
    # kg_builder.repository_parser()

    # step4:  根据解析出来的json建图为graphdata文件(.graph 和.dc)
    # kg_builder.graph_build()

    # step5:  将.graph文件 导入
    kg_builder.neo4j_import_batch()
