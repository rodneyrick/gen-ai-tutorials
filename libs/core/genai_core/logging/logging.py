import logging
import os
import aiofiles

LOG_FORMAT_DEFAULT = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT_DEFAULT)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
logging.getLogger('httpcore.http11').setLevel(logging.INFO)
logging.getLogger('httpcore.connection').setLevel(logging.INFO)
logging.getLogger('httpx').setLevel(logging.INFO)
logging.getLogger('openai._base_client').setLevel(logging.INFO)
logging.getLogger('langsmith.client').setLevel(logging.INFO)

class LogsConfigurations():
    LOG_PATH = "/var/tmp/genai/logs"

async def write_log(log_name, content):
    
    if not os.path.exists(LogsConfigurations.LOG_PATH):
        os.makedirs(LogsConfigurations.LOG_PATH)
        
    log_path = os.path.join(LogsConfigurations.LOG_PATH, log_name)
    
    async with aiofiles.open(log_path, 'a') as log_file:
        await log_file.write(content)