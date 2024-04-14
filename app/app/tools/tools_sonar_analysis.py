import requests
import json
from app.configs import logging, app_settings
from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from app.utils import parser_config_toml_files, paths

tools_settings = (
    app_settings.properties |
    parser_config_toml_files.run(
        config_name='tools', 
        dir_path=f"{paths.get_cwd(__file__)}/configs-toml"
    ) |
    parser_config_toml_files.run(
        config_name='tools-sonar', 
        dir_path=f"{paths.get_cwd(__file__)}/configs-toml"
    )
)

PATH_METRICS = f"{tools_settings['tools']['sonar']['SONAR_DIR']}{tools_settings['tools']['sonar']['analysis']['PATH_METRICS']}"
METRICS = tools_settings['tools']['sonar']['analysis']['METRICS']

logger = logging.getLogger()

class SonarAnalysisInput(BaseModel):
    token: str = Field(description="Sonar Token")
    project_name: str = Field(description="Name of project or project Key")
    url: str = Field(description="URL to sonarqube")
    metric_name: str = Field(description="Metric Name to generate insights")
    

class ToolSonarAnalysis(BaseTool):
    name = "sonar_analyzis"
    description = "useful for when you need to colect applications metrics in the sonarqube"
    args_schema: Type[BaseModel] = SonarAnalysisInput
    return_direct: bool = True

    def _run(self, metric_name: str, url: str, project_name: str, token: str,  
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            metrics = self.analyze_metrics(metric_name=metric_name, project_name=project_name, url=url, token=token)
            result = ""
            for evaluation in metrics:
                result += f"- {evaluation}\n"
        
            return result
        except Exception as e:
            logger.error(e)
            return False

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    def analyze_metrics(self, metric_name: str, project_name: str, token: str, url: str):
        results = []
        if metric_name in METRICS:
            with open(f'{PATH_METRICS}{metric_name}.json', 'r') as arquivo:
                json_data = json.load(arquivo)
                for componente in json_data['Metrics']:
                    result = self.request_metrics(metric_key=componente['key'], project_name=project_name,token=token, url=url)
                    results.append(result)
            return results
        raise Exception(f"{metric_name} não é uma opção válida: {METRICS}")
                    
    def request_metrics(self, metric_key: str, project_name: str, token: str, url: str):
        response = requests.get(
            f"{url}/api/measures/component?component={project_name}&metricKeys={metric_key}",
            headers={"Authorization": f"Bearer {token}"},
        )

        return self.get_value_metric(response=response.json(), metric_name=metric_key)
    
    def get_value_metric(self, response, metric_name):
        response = response["component"]["measures"]
        metric_value = response[0]["value"] if len(response) > 0 else 0
        
        return f'{metric_name}: {metric_value}'