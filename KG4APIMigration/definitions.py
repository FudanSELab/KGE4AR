import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
DATA_DIR = os.path.join(ROOT_DIR, 'data')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')


class LargeNEO4J:
    HOST = 'xxx'
    PORT = 'xxx'
    HTTPS = 'xxx'
    USERNAME = 'xxx'
    PASSWORD = 'xxx'
    URI = f'bolt://{HOST}:{PORT}'


class TestNEO4J:
    HOST = 'xxx'
    PORT = 'xxx'
    HTTPS = 'xxx'
    USERNAME = 'xxx'
    PASSWORD = 'xxx'
    URI = f'bolt://{HOST}:{PORT}'


class RemoteMilvus:
    HOST = 'xxx'
    PORT = 'xxx'
    MILVUS_TEST_COLLECTION = "xxx"