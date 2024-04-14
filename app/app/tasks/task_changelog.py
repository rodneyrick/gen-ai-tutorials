from app.configs import logging
from openai import OpenAI
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai
import os

logger = logging.getLogger()

from app.prompts import create_prompt_list
from textwrap import dedent

class TaskChangelog:
    def __init__(self, tools_repos, project_name: str, url_repo: str, range_commit: str):
        self.tools_repos = tools_repos
        self.project_name = project_name
        self.url_repo = url_repo
        self.range_commit = range_commit
        self.prompts = []
    
    def _run(self):
        self.commits = self.tools_repos.run(tool_input={
            "project_name": self.project_name, 
            "url": self.url_repo, 
            "function": 'git_commits_range_id', 
            "range_commit": self.range_commit
        })
        self.add_prompts()
        self.create_chat()

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

    @observe()
    def create_chat(self):

        # client = OpenAI(
        #     base_url=os.environ['OPENAI_BASE_URL'], 
        #     api_key=os.environ['OPENAI_API_KEY']
        # )
        
        langfuse_context.update_current_trace(
            tags=["task_changelog", f"repo: {self.project_name}"]
        )
        
        logger.debug(dedent(f"""
            Git Commits: 
            {self.commits}
        """))
        
        logger.info("Iniciando chat")
        completion = openai.chat.completions.create(
            model=os.environ['OPENAI_MODEL_NAME'],
            messages=self.prompts,
            temperature=0.3,
            user_id=os.environ['LANGFUSE_USER_ID'],
            tags=["task-changelog"]
        )
        logger.info(completion.choices[0].message.content)