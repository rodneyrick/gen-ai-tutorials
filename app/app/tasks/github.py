
import requests
import re

class ScientificEvaluation:
    def __init__(self, org_or_user: str="", git_token: str="", sonar_token: str="") -> None:
        self.base_url = "https://api.github.com"
        self.organization_name = org_or_user
        self.git_token = git_token
        self.sonar_token = sonar_token
 
    def make_evaluation(self, repository_name):
        evaluation = {"name": repository_name}
        evaluation["languages"] = self.get_languages_of_repository(repository_name)
        evaluation["quantity_of_pull_requests"] = self.get_quantity_of_pull_requests(
            repository_name
        )

        commits = self.get_commits(repository_name)
        commits_info = self.get_commits_information(commits)
        evaluation["quantity_of_commits"] = commits_info["quantity"]
        commits_checked = self.check_commit_pattern(commits_info["commit_messages"])
        evaluation["commit_pattern_percent"] = commits_checked[
            "percentage_of_commits_with_pattern"
        ]
        evaluation["commits_per_type_percent"] = commits_checked[
            "commits_per_type_percentage"
        ]
        
        return evaluation
    
    def make_request(self, url, parameter: str=""):
        """
        Realiza uma solicitação HTTP do tipo GET e retorna o resultado como JSON.
        Trata a paginação, caso tenha novas páginas, com mais registros, adiciona à lista de resultados.

        Args:
            url (str): A URL para a qual a solicitação GET será feita.

        Returns:
            list: Uma lista contendo os resultados da solicitação HTTP.
        """
        full_path = f"{self.base_url}/{url}?{parameter}&per_page=20&page="
        result = []
        page = 1
        rel_next = True

        while rel_next:
            response = requests.get(
                full_path + f"{page}",
                headers={"Authorization": f"Bearer {self.git_token}"},
            )

            result += response.json()

            if response.headers.get(
                "Link"
            ) is not None and 'rel="next"' in response.headers.get("Link"):
                page += 1
            else:
                rel_next = False

        return result

    def get_repository_info(self, repository_name, extra_path=None, parameter: str=""):
        """
        Busca informações sobre certo repositório, pode receber um extra_path para retornar
        informações específicas sobre o mesmo.

        Args:
            repository_name (str): Nome do repositório sobre o qual as informações serão resgatadas.
            extra_path (str): Caminho de url adicional, para buscar informações específicas sobre repositório.

        Returns:
            (list|obj): Retorna uma lista com informações sobre um repositório.
        """
        path = f"repos/{self.organization_name}/{repository_name}{extra_path if extra_path else ''}"
        repository = self.make_request(path, parameter=parameter)
        return repository

    def get_languages_of_repository(self, repository_name):
        """
        Busca quais são as linguagens utilizadas por um repositório.

        Args:
            repository_name (str): Nome do repositório sobre o qual as informações serão resgatadas.

        Returns:
            list: Retorna uma lista com as linguagens utilizadas no projeto.
        """
        not_languages = ["HTML", "CSS", "Roff"]
        languages = self.get_repository_info(repository_name, "/languages")
        return [language for language in languages if language not in not_languages]

    def get_commits(self, repository_name):
        """
        Busca informações sobre os commits de repositório.

        Args:
            repository_name (str): Nome do repositório sobre o qual as informações serão resgatadas.

        Returns:
            list: Retorna uma lista de objetos que possuem informações sobre os commits.
        """
        commits = self.get_repository_info(repository_name, "/commits")
        return commits

    def get_commits_information(self, commits: list):
        """
        Retira as mensagens da lista de objetos com informações de commits, coloca em uma lista, e conta a quantidade de commits.

        Args:
            commits (list): Lista de objetos com informações sobre commits

        Returns:
            obj: Objeto com a chave "commit_messages", que é uma lista com todas as mensagens de commit, e a chave "quantity", que traz a quantidade de commits do repositório
        """
        quantity_of_commits = 0
        commit_messages = []

        for commit in commits:
            quantity_of_commits += 1
            commit_messages.append(commit["commit"]["message"])

        return {"commit_messages": commit_messages, "quantity": quantity_of_commits}

    def check_commit_pattern(self, list_of_commits):
        """
        Recebe a lista com mensagens dos commits, aplica uma expressão regular para avaliar se
        atende ao padrão de commit, e chama outras funções, para retornar a porcentagem de commits
        que estão padronizados, quantidade de commits por tipo, e porcentagem de commits por tipo.

        Args:
            list_of_commits (list): lista com mensagens de commit

        Returns:
            obj: objeto contendo uma chave de porcentagem de commits no padrão, commits por tipo
            e porcentagem de commits por tipo, todos com valores numéricos, com no máximo 2 casas após a virgula.
        """
        commits_per_type = {}
        commit_pattern = re.compile(
            r"^(docs|doc|fix|style|feat|refactor|perf|test|build|ci|chore|revert)(\(.*\))?:(\s){0,4}(\S){1}(.|\n)*$"
        )
        commits_with_pattern = 1
        commits_without_pattern = 0
        for commit_message in list_of_commits[:-1]:
            if commit_pattern.match(commit_message):
                commit_type = self.get_commit_type(commit_message)
                commits_per_type[commit_type] = commits_per_type.get(commit_type, 0) + 1
                commits_with_pattern += 1
            else:
                commits_without_pattern += 1

        total = commits_without_pattern + commits_with_pattern
        percentage_of_commits_with_pattern = round(
            (commits_with_pattern / total) * 100, 2
        )

        commits_per_type_percentage = self.get_commits_per_type_percentage(
            commits_per_type
        )

        return {
            "percentage_of_commits_with_pattern": percentage_of_commits_with_pattern,
            "commits_per_type": commits_per_type,
            "commits_per_type_percentage": commits_per_type_percentage,
        }
        
    def get_commit_type(self, commit_message):
        """
        Recebe a mensagem de commit e retira o tipo do commit baseado em expressão regular

        Args:
            commit_message (str): texto com a mensagem de commit

        Returns:
            str: texto com o tipo do commit
        """
        type_pattern = re.compile(f"^[a-zA-Z]+")
        commit_type = type_pattern.search(commit_message)
        return commit_type[0]

    def get_commits_per_type_percentage(self, commits_per_type):
        """
        Recebe um objeto de commits por tipo e converte esses valores de quantidade, para porcentagem.

        Args:
            commits_per_type (obj): objeto com chaves representando tipo de commit, e um valor numérico do tipo
            inteiro, que representa a quantidade.

        Returns:
            float: número que representa a porcentagem de commits por tipo
        """
        total_commits = sum(commits_per_type.values())

        commits_per_type_percentage = {}

        for type, count in commits_per_type.items():
            commits_per_type_percentage[type] = round((count / total_commits) * 100, 2)

        return commits_per_type_percentage

    def get_quantity_of_pull_requests(self, repository_name):
        """
        Busca a quantidade de pull requests de um repositório.

        Args:
            repository_name (str): Nome do repositório sobre o qual as informações serão resgatadas.

        Returns:
            int: Número de pull requests realizados no repositório.
        """
        pull_requests = self.get_repository_info(repository_name, "/pulls", "state=all")
        return len(pull_requests)

