import os
from dotenv import load_dotenv
import logging

from app.utils import parser_config_toml_files

LOG_FORMAT_DEFAULT = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT_DEFAULT)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
logging.getLogger('httpcore.http11').setLevel(logging.INFO)
logging.getLogger('httpcore.connection').setLevel(logging.INFO)
logging.getLogger('httpx').setLevel(logging.INFO)
logging.getLogger('openai._base_client').setLevel(logging.INFO)
logging.getLogger('langsmith.client').setLevel(logging.INFO)


class AppSettings:
    properties = parser_config_toml_files.run(
        config_name='app-config', 
        dir_path=os.path.abspath(os.path.dirname(__file__))
    )
