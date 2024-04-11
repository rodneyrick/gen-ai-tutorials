from langchain.prompts import PromptTemplate
from openai import OpenAI
import json

class TaskSonarqubeV2:
    
    def __init__(self, tools_repos: dict=[], tools_analyzis: dict=[], tools_scans: dict=[], tools_outputs: dict=[]):
        self.tools_repos = tools_repos
        self.tools_analyzis = tools_analyzis
        self.tools_outputs = tools_outputs
        self.tools_scan = tools_scans
    
    def _run(self):
        
        pass
    
    def tools_repos(self):
        for tool in self.tools_repos:
            tool._run()