from genai.tools import ToolGit, ToolSonarScanner
from genai.utils.commands import exec_commands
from asyncio import run, sleep, create_task, gather
from genai.tools.tools_configs import GitConfigurations
from genai.tasks import TaskChangelog
import os
from dotenv import load_dotenv
from genai_core.logging import logging

load_dotenv()
logger = logging.getLogger()

async def tool_git_clone():
    task1 = create_task(ToolGit().git_clone(repo_path=f'{GitConfigurations.REPOS_PATH}/fastapi-lib-observability', 
                                            url="https://github.com/lucasBritoo/fastapi-lib-observability"))
    task2 = create_task(ToolGit().git_clone(repo_path=f'{GitConfigurations.REPOS_PATH}/aws-harmony', 
                                            url="https://github.com/lucasBritoo/aws-harmony"))

    await gather(task1, task2)

async def tool_git_commit_by_range():
    task1 = create_task(ToolGit().git_commits_range_id(repo_path=f'{GitConfigurations.REPOS_PATH}/rdpy-observability', 
                                            url="https://github.com/lucasBritoo/rdpy-observability",
                                            range_commit="f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829"))
    task2 = create_task(ToolGit().git_commits_range_id(repo_path=f'{GitConfigurations.REPOS_PATH}/rdpy-observability', 
                                            url="https://github.com/lucasBritoo/rdpy-observability",
                                            range_commit="f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829"))

    results = await gather(task1, task2)

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

async def tool_sonar_scanner():
    task1 = create_task(ToolSonarScanner().arun(tool_input={"project_name":"aws-harmony",
                                                            "token": os.environ['SONAR_TOKEN'], 
                                                            "url": os.environ['SONAR_HOST']}))

    await gather(task1)
    
run(tool_sonar_scanner())