import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
DATA_DIR = os.path.join(ROOT_DIR, 'data')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')


class LargeNEO4J:
    HOST = '10.176.64.33'
    PORT = 5687
    HTTPS = 5474
    USERNAME = 'neo4j'
    PASSWORD = 'fdsefdse'
    URI = f'bolt://{HOST}:{PORT}'


class TestNEO4J:
    HOST = '10.176.64.33'
    PORT = 9123
    HTTPS = 9124
    USERNAME = 'neo4j'
    PASSWORD = 'fdsefdse'
    URI = f'bolt://{HOST}:{PORT}'


class RemoteMilvus:
    HOST = '10.176.34.89'
    PORT = '19530'
    MILVUS_TEST_COLLECTION = "migration_small_test"