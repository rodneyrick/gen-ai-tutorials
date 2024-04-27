from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type
import requests
import time
import os
import asyncio

from genai_core.telemetry import instrumented_trace, TraceInstruments
from genai_core.logging import logging
from genai.tools.tools_configs import GitConfigurations, SonarConfigurations
from genai.utils.commands import exec_command, exec_commands
from genai_core.requests.requests import HttpClient

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
    http_client: HttpClient = None

    def _run(self) -> str:
        """Use the tool."""
        raise NotImplementedError("custom_search does not support async")

    @instrumented_trace()
    async def _arun(self, url: str, project_name: str, token: str) -> str:
        """Use the tool asynchronously."""
        self.http_client = HttpClient.get_instance()
        
        if not await self.check_sonar_project(url=url, project_name=project_name, token=token):
            await self.create_sonar_project(url=url, project_name=project_name, token=token)
        
        self.create_sonar_project_properties(base_dir=f"{GitConfigurations.REPOS_PATH}/{project_name}", token=token,
                                             url=url, project_name=project_name)
        await self.make_sonarqube_analysis(base_dir=f"{GitConfigurations.REPOS_PATH}/{project_name}",
                                     url=url, token=token, project_name=project_name)
        logging.debug("Análise do repositorio foi executada e econtra-se disponível no sonarqube")

    @instrumented_trace(span_name="Checking Analysis Ready", type=TraceInstruments.INSTRUMENTS_EVENT, 
                        kind=TraceInstruments.SPAN_KIND_CLIENT, span_parameters=False)
    async def verify_analysis_ready(self, url: str, project_name: str, token: str):

        analysis_ready = False

        while not analysis_ready:
            
            response = await self.http_client.get(url=f"{url}/api/project_analyses/search?project={project_name}",
                                        headers={"Authorization": f"Bearer {token}"})
            
            if response.status_code != 200:
                logger.error("Error ao verificar se a analise do sonar-scanner esta completa")
                raise ValueError(response.content)
            
            data = response.json()
            analysis = data["analyses"]
            
            if analysis != []:
                analysis_ready = True
            await asyncio.sleep(1)

    @instrumented_trace(span_name="Creating Sonar Project", type=TraceInstruments.INSTRUMENTS_EVENT, 
                        kind=TraceInstruments.SPAN_KIND_CLIENT, span_parameters=False)
    async def create_sonar_project(self, url: str,token: str, project_name: str):
        response = await self.http_client.post(
            url=f"{url}/api/projects/create?project={project_name}&name={project_name}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            logger.error("Error ao criar projeto do sonarqube")
            raise ValueError(response.content)
        
        return True
    
    @instrumented_trace(span_name="Checking Sonar Project", type=TraceInstruments.INSTRUMENTS_EVENT, 
                        kind=TraceInstruments.SPAN_KIND_CLIENT, span_parameters=False)
    async def check_sonar_project(self, url: str,token: str, project_name: str):
    
        response = await self.http_client.get(
            url=f"{url}/api/projects/search?projects={project_name}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()

        if data['paging']['total'] > 0:
            return True
    
        return False
    
    @instrumented_trace(span_name="Install Sonar Scanner", kind=TraceInstruments.SPAN_KIND_CLIENT)
    async def install_sonar_scanner(self):
        logging.info('Não foi encontrada uma instalação do sonar-scanner. Iniciando processo de download')
        await exec_commands(comando=['curl', SonarConfigurations.SONAR_SCANNER_DOWNLOAD, '--output', f'{SonarConfigurations.SONAR_DIR}/{SonarConfigurations.SONAR_SCANNER_VERSION}.zip'], log_name="download_sonar_scanner.log")
        await exec_commands(comando=['unzip', '-o', f'{SonarConfigurations.SONAR_DIR}/{SonarConfigurations.SONAR_SCANNER_VERSION}.zip', '-d', SonarConfigurations.SONAR_DIR], log_name="unzip_sonar_scanner.log")
        os.remove(f'{SonarConfigurations.SONAR_DIR}/{SonarConfigurations.SONAR_SCANNER_VERSION}.zip')
    
    @instrumented_trace(span_name="Sending Repo Sonarqube", kind=TraceInstruments.SPAN_KIND_CLIENT)
    async def make_sonarqube_analysis(self, base_dir: str, project_name: str, url: str, token: str):
        logger.debug("Enviando repositório para o SonarQube")
        if not os.path.exists(SonarConfigurations.SONAR_SCANNER_PATH):
            await self.install_sonar_scanner()
            
        await exec_commands(comando=[f'{SonarConfigurations.SONAR_SCANNER_PATH}/bin/sonar-scanner'], log_name='exec_sonar_scanner.log', cwd=base_dir)
        await self.verify_analysis_ready(token=token, project_name=project_name, url=url)

    @instrumented_trace(span_name="Creating Sonar Properties", type=TraceInstruments.INSTRUMENTS_EVENT, 
                        kind=TraceInstruments.SPAN_KIND_CLIENT, span_parameters=False)
    def create_sonar_project_properties(self,base_dir: str, token: str, project_name: str, url: str):
        logger.info("Creating sonar-project.properties file")
        with open(f"{base_dir}/sonar-project.properties", "w") as file:
            file.write("sonar.sources=.\n")
            file.write(f"sonar.token={token}\n")
            file.write(f"sonar.host.url={url}\n")
            file.write(f"sonar.projectKey={project_name}\n")
            file.write("sonar.sourceEncoding=UTF-8\n")

