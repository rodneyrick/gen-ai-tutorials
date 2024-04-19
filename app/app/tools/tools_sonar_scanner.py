from langchain.pydantic_v1 import BaseModel, Field
from app.utils.commands import exec_command
from langchain.tools import BaseTool
from typing import Type
import requests
import time
import os

from app.configs import logging, GitConfigurations, SonarConfigurations
from app.telemetry import instrumented_trace
logger = logging.getLogger()

class SonarScannerInput(BaseModel):
    token: str = Field(description="Sonar Token")
    project_name: str = Field(description="Name of project or project Key")
    url: str = Field(description="URL to sonarqube")

class ToolSonarScanner(BaseTool):
    name = "sonar_scanner"
    description = "useful for when you need to scanner applications to sonarqube"
    args_schema: Type[BaseModel] = SonarScannerInput
    return_direct: bool = True

    @instrumented_trace
    def _run(self, url: str, project_name: str, token: str) -> str:
        """Use the tool."""
        try:
            
            self.create_sonar_project(url=url, project_name=project_name, token=token)
            self.create_sonar_project_properties(base_dir=f"{GitConfigurations.REPOS_PATH}/{project_name}", token=token,
                                                 url=url, project_name=project_name)
            self.make_sonarqube_analysis(base_dir=f"{GitConfigurations.REPOS_PATH}/{project_name}")
            self.verify_analysis_ready(token=token, project_name=project_name, url=url)
            logging.debug("Análise do repositorio foi executada e econtra-se disponível no sonarqube")
            return True
        except Exception as e:
            logger.error(e)
            raise ValueError(e)

    async def _arun(self) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    @instrumented_trace(type="event")
    def verify_analysis_ready(self, url: str, project_name: str, token: str):

        analysis_ready = False

        while not analysis_ready:
            
            response = requests.get(
                f"{url}/api/project_analyses/search?project={project_name}",
                headers={"Authorization": f"Bearer {token}"},
            )
            json_of_response = response.json()
            analysis = json_of_response["analyses"]
            
            if analysis != []:
                analysis_ready = True
            time.sleep(1)

    @instrumented_trace(type="event")
    def create_sonar_project(self, url: str,token: str, project_name: str):
        requests.post(
            f"{url}/api/projects/create?project={project_name}&name={project_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
    
    @instrumented_trace
    def make_sonarqube_analysis(self, base_dir):
        logger.debug("Enviando repositório para o SonarQube")
        if not os.path.exists(SonarConfigurations.SONAR_SCANNER_PATH):
            logging.info('Não foi encontrada uma instalação do sonar-scanner. Iniciando processo de download')
            exec_command(comando=['curl', SonarConfigurations.SONAR_SCANNER_DOWNLOAD, '--output', f'{SonarConfigurations.SONAR_DIR}/{SonarConfigurations.SONAR_SCANNER_VERSION}.zip'], log_path="download_sonar_scanner.log")
            exec_command(comando=['unzip', '-o', f'{SonarConfigurations.SONAR_DIR}/{SonarConfigurations.SONAR_SCANNER_VERSION}.zip', '-d', SonarConfigurations.SONAR_DIR], log_path="unzip_sonar_scanner.log")
            os.remove(f'{SonarConfigurations.SONAR_DIR}/{SonarConfigurations.SONAR_SCANNER_VERSION}.zip')
        exec_command(comando=[f'{SonarConfigurations.SONAR_SCANNER_PATH}/bin/sonar-scanner'], log_path='exec_sonar_scanner.log', cwd=base_dir)

    @instrumented_trace(type="event")
    def create_sonar_project_properties(self,base_dir: str, token: str, project_name: str, url: str):
        logger.info("Creating sonar-project.properties file")
        with open(f"{base_dir}/sonar-project.properties", "w") as file:
            file.write("sonar.sources=.\n")
            file.write(f"sonar.token={token}\n")
            file.write(f"sonar.host.url={url}\n")
            file.write(f"sonar.projectKey={project_name}\n")
            file.write("sonar.sourceEncoding=UTF-8\n")

