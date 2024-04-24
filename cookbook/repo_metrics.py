from genai.tasks.task_sonarqube import TaskSonarqube
from genai.tools import ToolSonarScanner, ToolSonarAnalysis, ToolGit
from genai_core.callbacks import ToollCallbackHanlder
from genai_core.logging import logging
from genai.tools.tools_configs import SonarDomains
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger()

logger.debug("Iniciando Task")
task = TaskSonarqube(tools_repos=ToolGit(),
                     tools_analysis=ToolSonarAnalysis(),
                     tools_scanners=ToolSonarScanner(),
                     callbacks=[ToollCallbackHanlder()],
                     project_name="rdpy-observability",
                     url_repo="https://github.com/lucasBritoo/rdpy-observability",
                     sonar_token=os.environ['SONAR_TOKEN'],
                     sonar_url="http://192.168.3.241/sonarqube",
                     metric_list=[SonarDomains.SONAR_DOMAIN_ISSUES])
task._run()