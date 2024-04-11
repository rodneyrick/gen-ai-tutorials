import logging
import os
from app.utils import exec_command
from app.configs import logging
from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

REPOS_PATH = "/workspaces/gen-ai-tutorials/app/tmp"
logger = logging.getLogger()

class GitInput(BaseModel):
    project_name: str = Field(description="Repository Name")
    url: str = Field(description="URL to Git Repository")
    
class ToolGit(BaseTool):
    name = "git"
    description = "useful for when you need to interact git repositories"
    args_schema: Type[BaseModel] = GitInput
    return_direct: bool = True

    def _run(self, url: str, project_name: str,  
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            repository_path = f'{REPOS_PATH}/{project_name}'
            if not os.path.exists(REPOS_PATH):
                os.mkdir(REPOS_PATH)
            
            if not os.path.exists(repository_path):
                exec_command(comando=['git', 'clone', url], log_path='clone_repo_git.log', cwd=REPOS_PATH)
            
            logging.debug('O clone do repositorio git foi executado com sucesso')
            return True
        except Exception as e:
            logger.error(e)
            return False

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
