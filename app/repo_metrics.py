import dotenv
from app.github import ScientificEvaluation
from app.sonar_evaluations import SonarEvaluations
from langchain.prompts import PromptTemplate
from langchain_community.llms.ollama import Ollama
import os

org_or_user="lucasBritoo"
repository_name="rede-neural-deteccao-fraude"

dotenv.load_dotenv()
sonar_token=os.environ['SONAR_TOKEN']
git_token=os.environ['GIT_TOKEN']
ollama_url=os.environ['OLLAMA_URL']
ollama_model="llama2"

def format_evaluation(data):
    formatted_string = ''
    for key, value in data.items():
        if key == 'commits_per_type_percent':
            value_str = ', '.join([f'{k}: {v}' for k, v in value.items()])
            value_str = f"[{value_str}]"
        elif isinstance(value, list):
            value_str = ', '.join(map(str, value))
        else:
            value_str = str(value)
        formatted_string += f"{key}: {value_str}\n"
    
    return formatted_string

def create_prompt():
    
    template = """
        Based on metrics from sonarqube [Sonarqube Metrics] and github [Github Metrics], generate valuable insights about this application.

        [Sonarqube Metrics]
        {sonar_metrics}
        
        [Github Metrics]
        {git_metrics}

    """
    
    prompt_template = PromptTemplate.from_template(template)
    return prompt_template

ic = ScientificEvaluation(org_or_user=org_or_user, git_token=git_token)
evaluation_git = ic.make_evaluation(repository_name=repository_name)

sonar = SonarEvaluations(sonar_token=sonar_token,project_name=repository_name,
                         github_url=f"https://github.com/{org_or_user}/{repository_name}")     
evaluation_sonar = sonar.make_evaluation()


llm = Ollama(model=ollama_model, base_url=ollama_url)
chain = create_prompt() | llm

print(chain.invoke(
    {
        "sonar_metrics": format_evaluation(evaluation_sonar),
        "git_metrics": format_evaluation(evaluation_git),
    }
))

# print(llm.invoke(create_prompt().format(metrics=f"{format_evaluation(evaluation_sonar)}")))  # Somente Sonar
