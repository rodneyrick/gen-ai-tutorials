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

import dotenv
from app.task_sonarqube import Task_Sonarqube
import os
import logging

LOG_FORMAT_DEFAULT = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT_DEFAULT)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
logging.getLogger('httpcore.http11').setLevel(logging.INFO)
logging.getLogger('httpcore.connection').setLevel(logging.INFO)
logging.getLogger('httpx').setLevel(logging.INFO)
logging.getLogger('openai._base_client').setLevel(logging.INFO)


org_or_user="rodneyrick"
repository_name="MO444-PatternRecognition-and-MachineLearning"

dotenv.load_dotenv()
sonar_token=os.environ['SONAR_TOKEN']
git_token=os.environ['GIT_TOKEN']
ollama_url=os.environ['OLLAMA_URL']
ollama_model="mistralai_mistral-7b-instruct-v0.2"

sonar = Task_Sonarqube(metric_json="/workspaces/gen-ai-tutorials/app/tools/sonarqube/metrics/tests.json",
                       ollama_url=ollama_url,
                       org_or_user=org_or_user,
                       repository_name=repository_name,
                       sonar_token=sonar_token)
sonar.create_chat()