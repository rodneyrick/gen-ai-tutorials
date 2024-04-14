"""
Utilitário para geração de insights usando métricas do sonarqube e github em um modelo LLM Ollama.

Os parâmetros de configuração estão descritos abaixo:

org_or_user = Nome da organização ou usuário do github. Este é o autor do repositório que deseja analisar
repository_name = Nome do repositório que deseja analisar

sonar_token = Token de acesso ao sonarqube  <https://docs.sonarsource.com/sonarqube/9.8/user-guide/user-account/generating-and-using-tokens/>
git_token = Token de acesso pessoal ao github <https://docs.github.com/pt/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>

ollama_url = Url de acesso a API do Ollama no qual o modelo esta sendo executado.
ollama_model = Nome do modelo usado.

"""

from app.tasks.task_sonarqube import TaskSonarqube
from app.tools import ToolSonarScanner, ToolSonarAnalysis, ToolGit
from app.tasks import TaskSonarqube
from app.configs import load_dotenv, logging
import os

load_dotenv()

logging.debug("Iniciando Task")
task = TaskSonarqube(tools_repos=ToolGit(),
                     tools_analysis=ToolSonarAnalysis(),
                     tools_scanners=ToolSonarScanner(),
                     project_name="fastapi-lib-observability",
                     url_repo="https://github.com/lucasBritoo/fastapi-lib-observability",
                     sonar_token=os.environ['SONAR_TOKEN'],
                     sonar_url="http://sonarqube:9000",
                     metric_name="complexity")
task._run()