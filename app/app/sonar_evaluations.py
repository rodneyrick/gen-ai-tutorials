import os
import requests
import time
from app.utils import exec_command
import logging

class SonarEvaluations:
    
    def __init__(self, sonar_token, project_name, github_url) -> None:
        self.sonar_token = sonar_token
        self.project_key = project_name
        self.project_name = project_name
        self.github_url = github_url
        self.sonar_url = "http://sonarqube:9000"
        self.repos_path = "/workspaces/gen-ai-tutorials/app/tmp"
        self.sonar_scanner_path = "/workspaces/gen-ai-tutorials/app/tools/sonarqube/sonar-scanner-5.0.1.3006-linux"
        self.sonar_scanner_donwload = "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip?_gl=1*8egwxx*_gcl_au*MTA0NjMwMjU1OS4xNzEyMTY4MTE0*_ga*MjE0NjI4OTI4NC4xNzEyMTY4MTE0*_ga_9JZ0GZ5TC6*MTcxMjMyNjM0MS40LjAuMTcxMjMyNjM0MS42MC4wLjA."
        self.sonar_dir = "/workspaces/gen-ai-tutorials/app/tools/sonarqube"
        self.sonar_scanner_version = "sonar-scanner-5.0.1.3006-linux"

    def make_evaluation(self):
        """
        Realiza uma avaliação do projeto no SonarQube e retorna diversas métricas de qualidade de código.

        Returns:
            dict: Um dicionário contendo métricas como número total de issues, quantidade de issues por severidade,
                  porcentagem de duplicação de código, quantidade de hotspots de segurança, entre outras.
        """
        evaluation = {}
        self.create_sonar_project()
        self.dowload_github_files(github_url=self.github_url, repository_path=f'{self.repos_path}/{self.project_name}')
        self.create_sonar_project_properties(base_dir=f"{self.repos_path}/{self.project_name}")
        self.make_sonarqube_analysis(base_dir=f"{self.repos_path}/{self.project_name}")
        
        analysis_ready = False

        while not analysis_ready:
            analysis = self.make_request(
                "project_analyses/search", f"project={self.project_key}"
            )["analyses"]
            if analysis != []:
                analysis_ready = True
            time.sleep(1)

        evaluation["code_duplication"] = self.get_code_duplication()
        evaluation["maintainability_issues"] = self.get_quantity_of_maintainability_issues()
        evaluation["reliability_issues"] = self.get_quantity_of_reliability_issues()
        evaluation["security_issues"] = self.get_quantity_of_security_issues()
        evaluation["quantity_of_security_hotspots"] = self.get_quantity_of_security_hotspots()
        evaluation["quantity_of_bugs"] = self.get_bug_issues()
        evaluation["quantity_of_vulnerabilities"] = self.get_vulnerabiity_issues()
        evaluation["quantity_of_code_smells"] = self.get_code_smells_issues()

        return evaluation

    def make_request(self, extra_path, query):
        """
        Realiza uma requisição à API do SonarQube, já com a autenticação necessária e organizando parâmetros e queries.

        Args:
            extra_path (str): Caminho adicional para a requisição.
            query (str): Parâmetros de consulta para a requisição.

        Returns:
            dict: Resposta da requisição em formato JSON.
        """
        response = requests.get(
            f"{self.sonar_url}/api/{extra_path}?{query}",
            headers={"Authorization": f"Bearer {self.sonar_token}"},
        )
        json_of_response = response.json()
        return json_of_response

    def create_sonar_project(self):
        """
        Cria um projeto no SonarQube.

        Returns:
            None
        """
        requests.post(
            f"{self.sonar_url}/api/projects/create?project={self.project_name}&name={self.project_key}",
            headers={"Authorization": f"Bearer {self.sonar_token}"},
        )
    
    def dowload_github_files(self, github_url, repository_path="./tmp"):
        """
        Baixa os arquivos do repositório GitHub e coloca na pasta correta para análise do SonarQube,
        além de fazer o tratamento e apagar os arquivos para baixar os próximos.

        Args:
            github_url (str): URL do repositório GitHub.
            repository_path (str): Caminho onde os arquivos do repositório serão salvos.

        Returns:
            None
        """
        if not os.path.exists(self.repos_path):
            os.mkdir(self.repos_path)
        
        if not os.path.exists(repository_path):
            exec_command(comando=['git', 'clone', github_url], log_path='clone_repo_git.log', cwd=self.repos_path)
        
        logging.debug('O clone do repositorio git foi executado com sucesso')

    def make_sonarqube_analysis(self, base_dir):
        """
        Realiza uma análise do projeto no SonarQube, baseado no docker-compose configurado.

        Returns:
            None
        """
        if not os.path.exists(self.sonar_scanner_path):
            logging.info('Não foi encontrada uma instalação do sonar-scanner. Iniciando processo de download')
            exec_command(comando=['curl', self.sonar_scanner_donwload, '--output', f'{self.sonar_dir}/{self.sonar_scanner_version}.zip'], log_path="download_sonar_scanner.log")
            exec_command(comando=['unzip', '-o', f'{self.sonar_dir}/{self.sonar_scanner_version}.zip', '-d', self.sonar_dir], log_path="unzip_sonar_scanner.log")
            os.remove(f'{self.sonar_dir}/{self.sonar_scanner_version}.zip')
        exec_command(comando=[f'{self.sonar_scanner_path}/bin/sonar-scanner'], log_path='exec_sonar_scanner.log', cwd=base_dir)
        logging.debug("Análise do repositorio foi executada e econtra-se disponível no sonarqube")
    
    def create_sonar_project_properties(self,base_dir):
        """
        Cria o arquivo de propriedades do projeto SonarQube.

        Args:
            sonar_sources (str): Caminho para os arquivos fonte do projeto.
            sonar_host_url (str): URL do host do SonarQube.

        Returns:
            None
        """
        with open(f"{base_dir}/sonar-project.properties", "w") as file:
            file.write(f"sonar.sources=.\n")
            file.write(f"sonar.token={self.sonar_token}\n")
            file.write(f"sonar.host.url={self.sonar_url}\n")
            file.write(f"sonar.projectKey={self.project_key}\n")
            file.write("sonar.sourceEncoding=UTF-8\n")
            
    def get_value_of_component_response(self, response):
        """
        Obtém o valor de uma resposta de componente.

        Args:
            response (dict): Resposta da requisição em formato JSON.

        Returns:
            dict: dicionário com dados retornados pelo json.
        """
        response = response["component"]["measures"]
        return response[0]["value"] if len(response) > 0 else 0

    def get_code_duplication(self):
        """
        Obtém a porcentagem de duplicação de código.

        Returns:
            float: Porcentagem de duplicação de código.
        """
        code_duplication = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=duplicated_lines_density",
        )
        return self.get_value_of_component_response(code_duplication)

    def get_quantity_of_reliability_issues(self):
        """
        Obtém a quantidade de issues de confiabilidade.

        Returns:
            dict: Quantidade de issues de confiabilidade, separado em chaves que dizem o nível severidade e valor com quantidade.
        """
        reliability_issues = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=reliability_issues",
        )
        return self.get_value_of_component_response(reliability_issues)

    def get_quantity_of_security_issues(self):
        """
        Obtém a quantidade de issues de segurança.

        Returns:
            int: Quantidade de issues de segurança, separado em chaves que dizem o nível severidade e valor com quantidade..
        """
        security_issues = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=security_issues",
        )
        return self.get_value_of_component_response(security_issues)

    def get_quantity_of_maintainability_issues(self):
        """
        Obtém a quantidade de issues de manutenibilidade.

        Returns:
            int: Quantidade de issues de manutenibilidade, separado em chaves que dizem o nível severidade e valor com quantidade..
        """
        maintainability_issues = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=maintainability_issues",
        )
        return self.get_value_of_component_response(maintainability_issues)

    def get_quantity_of_security_hotspots(self):
        """
        Obtém a quantidade de hotspots de segurança.

        Returns:
            int: Quantidade de hotspots de segurança.
        """
        security_hotspots = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=security_hotspots",
        )
        return self.get_value_of_component_response(security_hotspots)

    def get_bug_issues(self):
        """
        Obtém a quantidade de issues de bugs.

        Returns:
            int: Quantidade de issues de bugs.
        """
        bugs = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=bugs",
        )
        return self.get_value_of_component_response(bugs)

    def get_code_smells_issues(self):
        """
        Obtém a quantidade de issues de smells de código.

        Returns:
            int: Quantidade de issues de smells de código.
        """
        code_smells = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=code_smells",
        )
        return self.get_value_of_component_response(code_smells)

    def get_vulnerabiity_issues(self):
        """
        Obtém a quantidade de issues de vulnerabilidades.

        Returns:
            int: Quantidade de issues de vulnerabilidades.
        """
        vulnerability_issues = self.make_request(
            extra_path="measures/component",
            query=f"component={self.project_key}&metricKeys=vulnerabilities",
        )
        return self.get_value_of_component_response(vulnerability_issues)
