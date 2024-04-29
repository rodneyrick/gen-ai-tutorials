from genai.tools import ToolGit, ToolSonarScanner, ToolSonarAnalysis
from genai.tasks import TaskChangelog, TaskSonarqube
from asyncio import run, sleep, create_task, gather
from genai.tools.tools_configs import SonarDomains
from genai_core.logging import logging
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger()

async def task_changelog():
    changelog1 = TaskChangelog(tools_repos=ToolGit(),
                     project_name="rdpy-observability",
                     url_repo="https://github.com/lucasBritoo/rdpy-observability",
                     range_commit="f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829")
    
    changelog2 = TaskChangelog(tools_repos=ToolGit(),
                     project_name="aws-harmony",
                     url_repo="https://github.com/lucasBritoo/aws-harmony",
                     range_commit="7c389a0f59a6ad3e606f365f690dfc2d04e742ec..c51deed33db38daec1af148e5872022541e34fbc")
    
    changelog3 = TaskChangelog(tools_repos=ToolGit(),
                     project_name="fastapi-lib-observability",
                     url_repo="https://github.com/lucasBritoo/fastapi-lib-observability",
                     range_commit="771b397d8e8343c41a212adad32598a737d8c635..1e3575b5111e7524e38c4878b64878ea3d6d18dc")
    
    task1 = create_task(changelog1._run())
    task2 = create_task(changelog2._run())
    task3 = create_task(changelog3._run())
    
    
    await gather(task1, task2, task3)

async def task_metrics():
    sonarqube1 = TaskSonarqube(tools_repos=ToolGit(),
                               tools_analysis=ToolSonarAnalysis(),
                               tools_scanners=ToolSonarScanner(),
                               project_name="rdpy-observability",
                               url_repo="https://github.com/lucasBritoo/rdpy-observability",
                               sonar_token=os.environ['SONAR_TOKEN'],
                               sonar_url="http://192.168.3.241/sonarqube",
                               metric_list=[SonarDomains.SONAR_DOMAIN_COMPLEXITY])
    
    sonarqube2 = TaskSonarqube(tools_repos=ToolGit(),
                               tools_analysis=ToolSonarAnalysis(),
                               tools_scanners=ToolSonarScanner(),
                               project_name="aws-harmony",
                               url_repo="https://github.com/lucasBritoo/aws-harmony",
                               sonar_token=os.environ['SONAR_TOKEN'],
                               sonar_url="http://192.168.3.241/sonarqube",
                               metric_list=[SonarDomains.SONAR_DOMAIN_ISSUES])
    
    sonarqube3 = TaskSonarqube(tools_repos=ToolGit(),
                               tools_analysis=ToolSonarAnalysis(),
                               tools_scanners=ToolSonarScanner(),
                               project_name="fastapi-lib-observability",
                               url_repo="https://github.com/lucasBritoo/fastapi-lib-observability",
                               sonar_token=os.environ['SONAR_TOKEN'],
                               sonar_url="http://192.168.3.241/sonarqube",
                               metric_list=[SonarDomains.SONAR_DOMAIN_SECURITY])
    
    task1 = create_task(sonarqube1._run())
    task2 = create_task(sonarqube2._run())
    task3 = create_task(sonarqube3._run())
    
    await gather(task1, task2, task3)

run(task_metrics())