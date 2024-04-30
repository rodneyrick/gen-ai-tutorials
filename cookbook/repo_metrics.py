from genai.tasks.task_sonarqube import TaskSonarqube
from genai_core.logging import logging
from genai.tools.tools_configs import SonarDomains
from dotenv import load_dotenv
from asyncio import run, create_task, gather

load_dotenv()
logger = logging.getLogger()

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

logger.debug("Iniciando Task")
run(task_metrics())