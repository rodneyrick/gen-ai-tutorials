from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.tools import BaseTool
from typing import Optional, Type
from enum import Enum
import os

from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai.tools.tools_configs import GitConfigurations
from genai_core.shell import ShellClient
from genai_core.logging import logging 

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
    shell_client: ShellClient = None

    def _run(self) -> str:
        """Use the tool."""
        raise NotImplementedError("custom_search does not support sync")

    @instrumented_trace()
    async def _arun(self, url: str, project_name: str, function: GitFunctionalities, range_commit: Optional[str] = None) -> str:
        """Use the tool asynchronously."""
        
        self.shell_client = ShellClient.get_instance()
        repo_path = f'{GitConfigurations.REPOS_PATH}/{project_name}'
        
        logger.debug(function)
        if function == GitFunctionalities.GIT_CLONE:
            result = await self.git_clone(repo_path=repo_path, url=url)
            return result
        
        result = await self.git_commits_range_id(repo_path=repo_path, url=url, range_commit=range_commit)
        return result
        
    @instrumented_trace(span_name="Git Clone", kind=TraceInstruments.SPAN_KIND_CLIENT)
    async def git_clone(self, repo_path, url):
        logger.debug(f"Repo Clone: {url}")
        if not os.path.exists(repo_path):
            await self.shell_client.exec(comando=['git', 'clone', url], log_name='clone_repo_git', 
                                cwd=GitConfigurations.REPOS_PATH)
        return True
    
    @instrumented_trace(span_name="Git Commits by Range", kind=TraceInstruments.SPAN_KIND_CLIENT)
    async def git_commits_range_id(self, repo_path, range_commit, url):
        await self.git_clone(repo_path=repo_path, url=url)
        
        logger.debug(f"Extract commits: {url}")
        comando = ['git', 'log', '--format=%B', '-n', str(GitConfigurations.MAX_COMMITS), range_commit]

        commits = await self.shell_client.exec(comando=comando, log_name="commits_by_range", cwd=repo_path, return_stdout=True)
        
        return self.format_commits(commits=commits)
        
    @instrumented_trace(span_name="Format Commits", type=TraceInstruments.INSTRUMENTS_EVENT, span_parameters=False)
    def format_commits(self, commits):
        
        linhas = commits.decode('utf-8').splitlines()
        linhas_limpa = filter(lambda linha: linha.strip() and not linha.startswith("Merge"), linhas)
        saida_str = '\n'.join(linhas_limpa)
        
        return saida_str

