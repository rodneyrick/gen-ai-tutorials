from textwrap import dedent
import os

from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.prompts import create_prompt_list
from genai_core.logging import logging

from genai.tools import ToolChatLLM

logger = logging.getLogger()

class TaskChangelog:
    def __init__(self, tools_repos, project_name: str, url_repo: str, range_commit: str):
        self.tools_repos = tools_repos
        self.project_name = project_name
        self.url_repo = url_repo
        self.range_commit = range_commit
        self.prompts = []
    
    @instrumented_trace()
    async def _run(self):
        self.commits = await self.tools_repos.arun(tool_input={
            "project_name": self.project_name, 
            "url": self.url_repo, 
            "function": 'git_commits_range_id', 
            "range_commit": self.range_commit
        })
        print(f"---> Finish: {self.url_repo}")
        # self.add_prompts()
        # self.create_chat()

    @instrumented_trace(span_name="Add Prompts Template")
    def add_prompts(self):
        self.prompts = create_prompt_list([
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
                    "commits": self.commits
                }
            }
        ])

    @instrumented_trace(span_name="Creating Chat", kind=TraceInstruments.SPAN_KIND_CLIENT)
    def create_chat(self):
        
        logger.debug("Create chat")
        
        chat = ToolChatLLM().run(tool_input={"model": os.environ['OPENAI_MODEL_NAME'], 
                                             "api_key": os.environ['OPENAI_API_KEY'],
                                             "api_base": os.environ['OPENAI_BASE_URL'],
                                             "prompt": self.prompts,
                                             "streaming": False})
        
        print(chat)
