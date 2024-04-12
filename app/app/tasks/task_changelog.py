from langchain.prompts import PromptTemplate
from app.configs import logging
from openai import OpenAI
import os

logger = logging.getLogger()

class TaskChangelog:
    def __init__(self, tools_repos, project_name: str, url_repo: str, range_commit: str):
        self.tools_repos = tools_repos
        self.project_name = project_name
        self.url_repo = url_repo
        self.range_commit = range_commit
    
    def _run(self):
        self.commits = self.tools_repos.run(tool_input={"project_name": self.project_name, "url": self.url_repo, 
                                         "function": 'git_commits_range_id', 
                                         "range_commit": self.range_commit})
        self.create_chat()
        
    def prompt_system(self):
        
        template = """
        You are a Git expert.
        Your skill is generating changelogs (documentation) based on commit messages in a specific repository.
        Provide a concise summary for updates, features, and bug fixes included in the commit in format markdown.\n
        """
        
        prompt_template = PromptTemplate.from_template(template)
        return prompt_template
        
    def prompt_user(self):
        template = """
        The [Commits] section contains commits messages.

        [Commits]
        {commits}\n
            
        """
        
        prompt_template = PromptTemplate.from_template(template)
        return prompt_template

    def create_chat(self):

        client = OpenAI(
            base_url=os.environ['OPENAI_BASE_URL'], 
            api_key=os.environ['OPENAI_API_KEY']
        )
        
        logger.info("Iniciando chat")
        completion = client.chat.completions.create(
            model=os.environ['OPENAI_MODEL_NAME'],
            messages=[
                {"role": "system", 
                "content": self.prompt_system().format()},
                {"role": "user", 
                "content": self.prompt_user().format(commits=self.commits)}
            ],
            temperature=0.3
        )
        logger.info(completion.choices[0].message.content)