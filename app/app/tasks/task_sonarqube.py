from langchain.prompts import PromptTemplate
from app.agents.create_chat import create_chat
from langchain_core.callbacks import BaseCallbackHandler
from app.configs import logging
import json
import os
from typing import List

from app.prompts import create_prompt_list
from app.tools import ToolChatLLM
from app.telemetry import instrumented_trace, TraceInstruments
from textwrap import dedent
from app.configs import logging, SonarConfigurations, SonarDomains

logger = logging.getLogger()

class TaskSonarqube:
    
    def __init__(self, tools_repos, tools_analysis, tools_scanners, 
                 project_name: str, url_repo: str, sonar_token: str, sonar_url: str,
                 metric_list: List[SonarDomains] = [],
                 callbacks: BaseCallbackHandler = None):
        self.tools_repos = tools_repos
        self.tools_analysis = tools_analysis
        self.tools_scanners = tools_scanners
        self.project_name = project_name
        self.url_repo = url_repo
        self.sonar_token = sonar_token
        self.sonar_url = sonar_url
        self.metrics_list = metric_list
        self.callbacks = callbacks

    @instrumented_trace()
    def _run(self):
        # self.tools_repos.run(tool_input={"project_name": self.project_name, "url": self.url_repo,
        #                                  "function": 'git_clone'},
        #                      callbacks=self.callbacks)

        # self.tools_scanners.run(tool_input={"project_name": self.project_name, "token": self.sonar_token, 
        #                                   "url": self.sonar_url},
        #                         callbacks=self.callbacks)
        
        for domain in self.metrics_list:
            
            logger.info(f"Selecting domain=`{domain}`")
            self.analysis = self.tools_analysis.run(tool_input={"project_name": self.project_name, "token": self.sonar_token,
                                                "url": self.sonar_url, "domain": domain},
                                                    callbacks=self.callbacks)
            
            json_data = self.get_info_from_json_file(domain.value)
            self.domain_name, self.domain_description = self.get_domain(json_data)
            metrics_description = self.extract_keys_and_descriptions(json_data)
            metrics_results = self.analysis
            
            logger.info("Iniciando chat")
            logger.debug(dedent(f"""
                Domain: {self.domain_name}
                Description: {self.domain_description}
                Metrics Description: 
                {metrics_description}
                Metrics: 
                {metrics_results}
            """))
            self.add_prompts(
                self.domain_name, 
                self.domain_description,
                metrics_description=metrics_description, 
                metrics_results=metrics_results
            )
            self._create_chat()

    @instrumented_trace(span_name="Add Prompts Template")
    def add_prompts(self, domain_name, domain_description, metrics_description, metrics_results):
        self.prompts = create_prompt_list([
            {
                "role": "system", 
                "content": dedent("""
                    You are a senior software engineer.
                    Your skill is to analyze metrics using the Sonarqube tool to provide valuable insights on areas that need improvement in a given application.
                    The metrics available belong to the {domain_name} domain. Please refer to the domain description to understand the context of the metrics: {domain_description}\n.
                """),
                "parameters": {
                    'domain_name': domain_name, 
                    'domain_description': domain_description
                }
            },
            {
                "role": "user", 
                "content": dedent("""
                    The [Description] section contains descriptions of each metric.
                    The [Metrics] section contains the metrics generated by the tool for a particular repository.
                        
                    [Description]
                    {metrics_description}\n\n
                        
                    [Metrics]
                    {metrics_results}\n
                """),
                "parameters": {
                    'metrics_description': metrics_description, 
                    'metrics_results': metrics_results
                }
            }
        ])

    @instrumented_trace(span_name="Load Domain Json", type=TraceInstruments.INSTRUMENTS_EVENT)
    def get_info_from_json_file(self, metric_json) -> dict:
        path_file_metric_json = f"{SonarConfigurations.PATH_METRICS}/{metric_json}"
        with open(path_file_metric_json, 'r') as arquivo:
            json_data = json.load(arquivo)
        return json_data

    @instrumented_trace(span_name="Reading METRIC and DESCRIPTION")
    def extract_keys_and_descriptions(self, json_data):
        logger.info("Reading METRIC and DESCRIPTION informations")
        metrics = json_data["Metrics"]
        result = "\n"
        for metric in metrics:
            result += f"- {metric['key']}: {metric['description']}\n"
        return result

    @instrumented_trace(span_name="Reading DOMAIN and CONTEXT", type=TraceInstruments.INSTRUMENTS_EVENT)
    def get_domain(self, json_data):
        logger.info("Reading DOMAIN and CONTEXT informations")
        return json_data['Domain'], json_data['Context']

    @instrumented_trace(span_name="Creating Chat", kind=TraceInstruments.SPAN_KIND_CLIENT)
    def _create_chat(self):
        logger.debug("Create chat")

        chat = ToolChatLLM().run(tool_input={"model": os.environ['OPENAI_MODEL_NAME'], 
                                             "api_key": os.environ['OPENAI_API_KEY'],
                                             "api_base": os.environ['OPENAI_BASE_URL'],
                                             "prompt": self.prompts,
                                             "streaming": False})
        
        print(chat)
    
