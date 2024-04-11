import os
import requests
import time
from app.utils import exec_command
import logging
from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

REPOS_PATH = "/workspaces/gen-ai-tutorials/app/tmp"
SONAR_SCANNER_PATH = "/workspaces/gen-ai-tutorials/app/tools/sonarqube/sonar-scanner-5.0.1.3006-linux"
SONAR_SCANNER_DONWLOAD = "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip?_gl=1*8egwxx*_gcl_au*MTA0NjMwMjU1OS4xNzEyMTY4MTE0*_ga*MjE0NjI4OTI4NC4xNzEyMTY4MTE0*_ga_9JZ0GZ5TC6*MTcxMjMyNjM0MS40LjAuMTcxMjMyNjM0MS42MC4wLjA."
SONAR_DIR = "/workspaces/gen-ai-tutorials/app/tools/sonarqube"
SONAR_SCANNER_VERSION = "sonar-scanner-5.0.1.3006-linux"

class SonarScannerInput(BaseModel):
    token: str = Field(description="Sonar Token")
    project_name: str = Field(description="Name of project or project Key")
    url: str = Field(description="URL to sonarqube")

class ToolSonarScanner(BaseTool):
    name = "sonar_scanner"
    description = "useful for when you need to scanner applications to sonarqube"
    args_schema: Type[BaseModel] = SonarScannerInput
    return_direct: bool = True

    def _run(self, url: str, project_name: str, token: str,  
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            
            self.create_sonar_project(url=url, project_name=project_name, token=token)
            self.create_sonar_project_properties(base_dir=f"{REPOS_PATH}/{project_name}", token=token,
                                                 url=url, project_name=project_name)
            self.make_sonarqube_analysis(base_dir=f"{REPOS_PATH}/{project_name}")
            self.verify_analysis_ready(token=token, project_name=project_name, url=url)
            return True
        except Exception as e:
            print(e)
            return False

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

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

    def create_sonar_project(self, url: str="http://localhost:9000",token: str=None, project_name: str=None):
        requests.post(
            f"{url}/api/projects/create?project={project_name}&name={project_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
    
    def make_sonarqube_analysis(self, base_dir):
        if not os.path.exists(SONAR_SCANNER_PATH):
            logging.info('Não foi encontrada uma instalação do sonar-scanner. Iniciando processo de download')
            exec_command(comando=['curl', SONAR_SCANNER_DONWLOAD, '--output', f'{SONAR_DIR}/{SONAR_SCANNER_VERSION}.zip'], log_path="download_sonar_scanner.log")
            exec_command(comando=['unzip', '-o', f'{SONAR_DIR}/{SONAR_SCANNER_VERSION}.zip', '-d', SONAR_DIR], log_path="unzip_sonar_scanner.log")
            os.remove(f'{SONAR_DIR}/{SONAR_SCANNER_VERSION}.zip')
        exec_command(comando=[f'{SONAR_SCANNER_PATH}/bin/sonar-scanner'], log_path='exec_sonar_scanner.log', cwd=base_dir)
        logging.debug("Análise do repositorio foi executada e econtra-se disponível no sonarqube")
    
    def create_sonar_project_properties(self,base_dir: str, token: str, project_name: str, url: str):
        with open(f"{base_dir}/sonar-project.properties", "w") as file:
            file.write(f"sonar.sources=.\n")
            file.write(f"sonar.token={token}\n")
            file.write(f"sonar.host.url={url}\n")
            file.write(f"sonar.projectKey={project_name}\n")
            file.write("sonar.sourceEncoding=UTF-8\n")

