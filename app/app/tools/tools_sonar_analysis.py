from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
from enum import Enum
import requests
import json

from app.configs import logging, SonarConfigurations, SonarDomains
logger = logging.getLogger()

class SonarAnalysisInput(BaseModel):
    token: str = Field(description="Sonar Token")
    project_name: str = Field(description="Name of project or project Key")
    url: str = Field(description="URL to sonarqube")
    metric_name: Enum = Field(description="Metric Name to generate insights")
    
class ToolSonarAnalysis(BaseTool):
    name = "sonar_analyzis"
    description = "useful for when you need to colect applications metrics in the sonarqube"
    args_schema: Type[BaseModel] = SonarAnalysisInput

    def _run(self, metric_name: Enum, url: str, project_name: str, token: str) -> str:
        try:
            metrics = self.analyze_metrics(metric_name=metric_name, project_name=project_name, url=url, token=token)
            result = self.format_result(metrics=metrics)
            return result
        
        except Exception as e:
            logger.error(e)
            raise ValueError(e)

    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")

    def analyze_metrics(self, metric_name: str, project_name: str, token: str, url: str):
        results = []
        if metric_name in SonarDomains:
            with open(f'{SonarConfigurations.PATH_METRICS}/{metric_name.value}', 'r') as arquivo:
                json_data = json.load(arquivo)
                for componente in json_data['Metrics']:
                    result = self.request_metrics(metric_key=componente['key'], project_name=project_name,token=token, url=url)
                    results.append(result)
            return results
        raise Exception(f"{metric_name} não é uma opção válida: {SonarDomains}")
                    
    def request_metrics(self, metric_key: str, project_name: str, token: str, url: str):
        response = requests.get(
            f"{url}/api/measures/component?component={project_name}&metricKeys={metric_key}",
            headers={"Authorization": f"Bearer {token}"},
        )

        return self.get_value_metric(response=response.json(), metric_name=metric_key)
    
    def get_value_metric(self, response, metric_name):
        response = response["component"]["measures"]
        metric_value = response[0]["value"] if len(response) > 0 else ""
        
        metric_value = metric_value.strip('{}')
        metric_value = metric_value.replace(',', ' | ')
        metric_value = metric_value.replace(':', ': ')
        return f'{metric_name}: {metric_value}'
        
    def format_result(self, metrics):
        result = ""
        for evaluation in metrics:
            result += f"- {evaluation}\n"

        return result