from genai.tools import ToolGit
from genai.tasks import TaskChangelog
from dotenv import load_dotenv
from genai_core.logging import logging

load_dotenv()

logger = logging.getLogger()
logger.debug("Iniciando Task")
task = TaskChangelog(tools_repos=ToolGit(),
                     project_name="rdpy-observability",
                     url_repo="https://github.com/lucasBritoo/rdpy-observability",
                     range_commit="f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829")
task._run()