from pydantic import BaseModel, Field
from typing import Optional, Any, List, Type
from textwrap import dedent
import os

from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.prompts import create_prompt_list
from genai_core.logging import logging
from genai_core.tools import BaseTool
from genai.tools import ToolChatLLM, GitFunctionalities

logger = logging.getLogger()

class TaskInput(BaseModel):
    project_name: str = Field(description="Repository Name")
    url: str = Field(description="URL to Git Repository")
    range_commit: Optional[str] = Field(description="Range Commit ID. Ex: 00000..1111", default=None)
    tool_repos: Any = Field(description="Tools Repo")
    
class TaskChangelog(BaseTool):
    name = "Task Changelog"
    description = "useful for when you need to generate changelog repositories"
    args_schema: Type[BaseModel] = TaskInput
    
    @instrumented_trace()
    async def _run(self, project_name, url, range_commit, tool_repos):
        commits = await tool_repos.run(tool_input={
            "project_name": project_name, 
            "url": url, 
            "function": GitFunctionalities.GIT_COMMITS_RANGE_ID, 
            "range_commit": range_commit
        })
        prompt = self.add_prompts(commits=commits)
        await self.create_chat(prompt)

    @instrumented_trace(span_name="Add Prompts Template", span_parameters=False)
    def add_prompts(self, commits):
        logger.debug("Iniciando Prompt")
        prompts = create_prompt_list([
            {
                "role": "system", 
                "content": dedent("""
                    You are a Git expert.
                    Your skill is generating changelogs (documentation) based on commit messages in a specific repository.
                    Provide a concise summary for updates, features, and bug fixes included in the commit in format markdown.\n
                """)
            },
            {
                "role": "user", 
                "content": dedent("""
                    The [Commits] section contains commits messages.

                    [Commits]
                    {commits}\n        
                """),
                "parameters": {
                    "commits": commits
                }
            }
        ])
        
        return prompts

    @instrumented_trace(span_name="Creating Chat", kind=TraceInstruments.SPAN_KIND_CLIENT)
    async def create_chat(self, prompt):
        
        logger.debug("Create chat")
        
        chat = await ToolChatLLM().run(tool_input={"model": os.environ['OPENAI_MODEL_NAME'], 
                                             "api_key": os.environ['OPENAI_API_KEY'],
                                             "api_base": os.environ['OPENAI_BASE_URL'],
                                             "prompt": prompt,
                                             "streaming": False})
        
        logger.debug(chat)
