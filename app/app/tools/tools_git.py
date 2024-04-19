from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.tools import BaseTool
from typing import Optional, Type
from enum import Enum
import subprocess
import os

from app.configs import logging, GitConfigurations
from app.utils.commands import exec_command
from app.telemetry import instrumented_trace
logger = logging.getLogger()

class GitFunctionalities(Enum):
    GIT_CLONE = "git_clone"
    GIT_COMMITS_RANGE_ID = "git_commits_range_id"

class GitInput(BaseModel):
    project_name: str = Field(description="Repository Name")
    url: str = Field(description="URL to Git Repository")
    function: GitFunctionalities = Field(description="Function to execution tool")
    range_commit: Optional[str] = Field(description="Range Commit ID. Ex: 00000..1111")
    
    @validator("range_commit", always=True)
    def check_range_commit(cls, v, values):
        if values.get("function") == GitFunctionalities.GIT_COMMITS_RANGE_ID and v is None:
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

    @instrumented_trace()
    def _run(self, url: str, project_name: str, function: GitFunctionalities, range_commit: Optional[str] = None) -> str:
        """Use the tool."""
        try:
            self.repo_path = f'{GitConfigurations.REPOS_PATH}/{project_name}'
            self.url = url
            self.range_commit = range_commit

            method = getattr(self, function.value, None)
            
            if not method:
                raise Exception(f'Metodo nao encontrado: {function}')
            
            return method()
                
        except Exception as e:
            logger.error(e)
            raise ValueError(e)

    async def _arun(self) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    @instrumented_trace()
    def git_clone(self):
        
        if not os.path.exists(GitConfigurations.REPOS_PATH):
            os.mkdir(GitConfigurations.REPOS_PATH)
        
        if not os.path.exists(self.repo_path):
            exec_command(comando=['git', 'clone', self.url], log_path='clone_repo_git.log', cwd=GitConfigurations.REPOS_PATH)
        
        logging.debug('O clone do repositorio git foi executado com sucesso')
        return True
    
    @instrumented_trace()
    def git_commits_range_id(self):
        self.git_clone()
        
        comando = ['git', 'log', '--format=%B', '-n', str(GitConfigurations.MAX_COMMITS), self.range_commit]

        with subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.repo_path) as processo:
            commits, _ = processo.communicate()

        linhas = commits.decode('utf-8').splitlines()
        linhas_limpa = filter(lambda linha: linha.strip() and not linha.startswith("Merge"), linhas)
        saida_str = '\n'.join(linhas_limpa)

        return saida_str

