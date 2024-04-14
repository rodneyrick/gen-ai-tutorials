import logging
import os
from app.utils.commands import exec_command
from app.configs import logging, app_settings
from typing import Optional, Type, Literal
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.tools import BaseTool
import subprocess

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from app.utils import parser_config_toml_files, paths

tools_settings = (
    app_settings.properties |
    parser_config_toml_files.run(
        config_name='tools', 
        dir_path=f"{paths.get_cwd(__file__)}/configs-toml"
    ) |
    parser_config_toml_files.run(
        config_name='tools-git', 
        dir_path=f"{paths.get_cwd(__file__)}/configs-toml"
    )
)

REPOS_PATH = tools_settings['default']['REPOS_PATH']
MAX_COMMITS = tools_settings['tools']['git']['MAX_COMMITS']

logger = logging.getLogger()

Functionalities = Literal["git_clone", "git_commits_range_id"]

class GitInput(BaseModel):
    project_name: str = Field(description="Repository Name")
    url: str = Field(description="URL to Git Repository")
    function: Functionalities = Field(description="Function to execution tool")
    range_commit: Optional[str] = Field(description="Range Commit ID. Ex: 00000..1111")
    
    @validator("range_commit", always=True)
    def check_range_commit(cls, v, values):
        if values.get("function") == "git_commits_range_id" and v is None:
            raise ValueError("range_commit é obrigatório quando o parâmetro function é definido como git_commits_range_id")
        return v
    
class ToolGit(BaseTool):
    name = "git"
    description = "useful for when you need to interact git repositories"
    args_schema: Type[BaseModel] = GitInput
    return_direct: bool = True
    repo_path: str = ""
    url: str = ""
    range_commit: str = ""

    def _run(self, url: str, project_name: str, function: str, range_commit: Optional[str] = None,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            self.repo_path = f'{REPOS_PATH}/{project_name}'
            self.url = url
            self.range_commit = range_commit

            method = getattr(self, function, None)
            
            if not method:
                raise Exception(f'Metodo nao encontrado: {function}')
            
            return method()
                
        except Exception as e:
            logger.error(e)
            return False

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    def git_clone(self):
        
        if not os.path.exists(REPOS_PATH):
            os.mkdir(REPOS_PATH)
        
        if not os.path.exists(self.repo_path):
            exec_command(comando=['git', 'clone', self.url], log_path='clone_repo_git.log', cwd=REPOS_PATH)
        
        logging.debug('O clone do repositorio git foi executado com sucesso')
        return True
    
    def git_commits_range_id(self):
        self.git_clone()
        
        comando = ['git', 'log', '--format=%B', '-n', MAX_COMMITS, self.range_commit]

        with subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.repo_path) as processo:
            commits, _ = processo.communicate()

        linhas = commits.decode('utf-8').splitlines()
        linhas_limpa = filter(lambda linha: linha.strip() and not linha.startswith("Merge"), linhas)
        saida_str = '\n'.join(linhas_limpa)

        return saida_str

