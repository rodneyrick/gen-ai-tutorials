from app.tools import ToolGit
from app.tasks import TaskChangelog
from app.configs import load_dotenv, logging

load_dotenv()

logging.debug("Iniciando Task")
task = TaskChangelog(tools_repos=ToolGit(),
                     project_name="rdpy-observability",
                     url_repo="https://github.com/lucasBritoo/rdpy-observability",
                     range_commit="f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829")
task._run()