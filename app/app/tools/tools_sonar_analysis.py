from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
from enum import Enum
import requests
import json

from app.configs import logging, SonarConfigurations, SonarDomains
from app.telemetry import instrumented_trace, TraceInstruments
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

    @instrumented_trace()
    def _run(self, domain: Enum, url: str, project_name: str, token: str) -> str:
        try:
            metrics = self.analyze_metrics(domain=domain, project_name=project_name, url=url, token=token)
            return self.format_result(metrics)

        except Exception as e:
            logger.error(e)
            raise ValueError(e)

    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")

    @instrumented_trace(span_name="Analyis Metrics")
    def analyze_metrics(self, domain: SonarDomains, project_name: str, token: str, url: str):
        results = []
        with open(f'{SonarConfigurations.PATH_METRICS}/{domain.value}', 'r') as arquivo:
            json_data = json.load(arquivo)
            for componente in json_data['Metrics']:
                result = self.request_metrics(metric_name=componente['key'], project_name=project_name,token=token, url=url)
                results.append(result)
        return results

    @instrumented_trace(span_name="Request Metric", kind=TraceInstruments.SPAN_KIND_CLIENT)
    def request_metrics(self, metric_name: str, project_name: str, token: str, url: str):
        response = requests.get(
            f"{url}/api/measures/component?component={project_name}&metricKeys={metric_name}",
            headers={"Authorization": f"Bearer {token}"},
        )

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