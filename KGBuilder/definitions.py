import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

# project data
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# the output dir
KG_DIR = os.path.join(DATA_DIR, 'kg')
KG_CSV_DIR = "/home/lmw/disk_mount_dir/APIKG_Yyj/neo4j-community-4.4.4/import"
SCRIPT_DIR = os.path.join(ROOT_DIR, 'script')
LOG_FILE = os.path.join(DATA_DIR, 'KGBuilder.log')

PROJECT_DIR = os.path.join(DATA_DIR, 'project')
REPOSITORIES_DIR = os.path.join(DATA_DIR, 'repository')
JAVA_REPOSITORIES_DIR = os.path.join(DATA_DIR, 'repository', "Java")

REPOSITORIES_PARSER_DIR = os.path.join(DATA_DIR, 'parseResult')

# jar configuration
JAR_PATH = os.path.join(SCRIPT_DIR, 'APISrcParser-1.0-SNAPSHOT.jar')


class CodeConstant:
    LABEL_CODE_ELEMENT = "code_element"
    QUALIFIED_NAME = "qualified_name"


class ThirdLibraryNeo4jConfigure:
    IP = "http://47.116.194.87:9004/"
    USERNAME = "neo4j"
    PASSWORD = "cloudfdse"

# 和neo4j登陆的界面ip不同的那个ip
class ExportNeo4jConfigure:
    IP = "http://47.116.194.87:9211"
    USERNAME = "neo4j"
    PASSWORD = "fdsefdse"
