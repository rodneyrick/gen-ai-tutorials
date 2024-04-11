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

from app import configs
from app.tasks.task_sonarqube import Task_Sonarqube

configs.load_dotenv()

org_or_user="rodneyrick"
repository_name="MO444-PatternRecognition-and-MachineLearning"

sonar = Task_Sonarqube(
    org_or_user=org_or_user,
    repository_name=repository_name,
    # metric_json_items=["tests"]
)
s = sonar.create_chat()
# s = sonar.create_chat()