from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
from enum import Enum
import json

from genai.tools.tools_configs import SonarConfigurations, SonarDomains
from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.requests import HttpClient
from genai_core.logging import logging

logger = logging.getLogger()

class SonarAnalysisInput(BaseModel):
    token: str = Field(description="Sonar Token")
    project_name: str = Field(description="Name of project or project Key")
    url: str = Field(description="URL to sonarqube")
    domain: SonarDomains = Field(description="Domain to generate insights")

class ToolSonarAnalysis(BaseTool):
    name = "sonar_analyzis"
    description = "useful for when you need to colect applications metrics in the sonarqube"
    args_schema: Type[BaseModel] = SonarAnalysisInput
    http_client: HttpClient = None

    @instrumented_trace()
    def _run(self) -> str:
        raise NotImplementedError("custom_search does not support sync")
    
    async def _arun(self, domain: Enum, url: str, project_name: str, token: str) -> str:
        self.http_client = HttpClient.get_instance()
        
        metrics = await self.analyze_metrics(domain=domain, project_name=project_name, url=url, token=token)
        return self.format_result(metrics)

    @instrumented_trace(span_name="Analyis Metrics")
    async def analyze_metrics(self, domain: SonarDomains, project_name: str, token: str, url: str):
        results = []
        with open(f'{SonarConfigurations.PATH_METRICS}/{domain.value}', 'r') as arquivo:
            json_data = json.load(arquivo)
            for componente in json_data['Metrics']:
                logger.debug(f"metric: {componente['key']}  domain: {domain}")
                result = await self.request_metrics(metric_name=componente['key'], project_name=project_name,token=token, url=url)
                results.append(result)
        return results

    @instrumented_trace(span_name="Request Metric", kind=TraceInstruments.SPAN_KIND_CLIENT)
    async def request_metrics(self, metric_name: str, project_name: str, token: str, url: str):
        
        response = await self.http_client.get(url=f"{url}/api/measures/component?component={project_name}&metricKeys={metric_name}",
                                             headers={"Authorization": f"Bearer {token}"})

        if response.status_code != 200:
            logger.error("Error ao realizar requisicao de metrica do sonarqube")
            raise ValueError(response.content)
            
        return self.get_value_metric(json_data=response.json(), metric_name=metric_name)

    @instrumented_trace(span_name="Get Value by Metric", type=TraceInstruments.INSTRUMENTS_EVENT, span_parameters=False)
    def get_value_metric(self, json_data, metric_name):
        json_data = json_data["component"]["measures"]
        metric_value = json_data[0]["value"] if len(json_data) > 0 else ""

        metric_value = metric_value.strip('{}')
        metric_value = metric_value.replace(',', ' | ')
        metric_value = metric_value.replace(':', ': ')
        return f'{metric_name}: {metric_value}'

    @instrumented_trace(span_name="Format Result", type=TraceInstruments.INSTRUMENTS_EVENT, span_parameters=False)
    def format_result(self, metrics):
        return "\n".join([f"- {metric}" for metric in metrics])