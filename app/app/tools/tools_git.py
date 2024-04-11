import logging
import os
from app.utils import exec_command

class ToolGit:
    
    def __init__(self, url,repository_name):
        self.url=url
        self.repository_name = repository_name
        self.repos_path = "/workspaces/gen-ai-tutorials/app/tmp"
        self.repository_path = f'{self.repos_path}/{self.repository_name}'
        
    def _run(self):

        if not os.path.exists(self.repos_path):
            os.mkdir(self.repos_path)
        
        if not os.path.exists(self.repository_path):
            exec_command(comando=['git', 'clone', self.url], log_path='clone_repo_git.log', cwd=self.repos_path)
        
        logging.debug('O clone do repositorio git foi executado com sucesso')