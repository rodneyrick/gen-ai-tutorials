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
    changelog1 = TaskChangelog().run(tool_input={
        "project_name": "rdpy-observability",
        "url": "https://github.com/lucasBritoo/rdpy-observability",
        "tool_repos": ToolGit(),
        "range_commit": "f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829"
    })
        
    changelog2 = TaskChangelog().run(tool_input={
        "project_name": "aws-harmony",
        "url": "https://github.com/lucasBritoo/aws-harmony",
        "tool_repos": ToolGit(),
        "range_commit": "7c389a0f59a6ad3e606f365f690dfc2d04e742ec..c51deed33db38daec1af148e5872022541e34fbc"
    })
                     
    changelog3 = TaskChangelog().run(tool_input={
        "project_name": "fastapi-lib-observability",
        "url":"https://github.com/lucasBritoo/fastapi-lib-observability",
        "tool_repos": ToolGit(),
        "range_commit": "771b397d8e8343c41a212adad32598a737d8c635..1e3575b5111e7524e38c4878b64878ea3d6d18dc"
    })
                    
    task1 = create_task(changelog1)
    task2 = create_task(changelog2)
    task3 = create_task(changelog3)
    
    
    await gather(task1, task2, task3)

async def task_metrics():
    sonarqube1 = TaskSonarqube().run(tool_input={
        "project_name": "rdpy-observability",
        "domains": [SonarDomains.SONAR_DOMAIN_COMPLEXITY]
    })

    sonarqube2 = TaskSonarqube().run(tool_input={
        "project_name": "aws-harmony",
        "domains": [SonarDomains.SONAR_DOMAIN_ISSUES]
    })
    
    sonarqube3 = TaskSonarqube().run(tool_input={
        "project_name": "fastapi-lib-observability",
        "domains": [SonarDomains.SONAR_DOMAIN_SECURITY]
    })
    
    task1 = create_task(sonarqube1)
    task2 = create_task(sonarqube2)
    task3 = create_task(sonarqube3)
    
    await gather(task1, task2, task3)

run(task_changelog())