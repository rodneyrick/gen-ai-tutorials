import requests
import json

class ToolSonarAnalyzis:
    
    def __init__(self, sonar_token: str="", project_name: str="") -> None:
        self.sonar_token = sonar_token
        self.project_key = project_name
        self.sonar_url = "http://sonarqube:9000"
        self.path_metrics = "/workspaces/gen-ai-tutorials/app/tools/sonarqube/metrics/"
        self.metrics = ['complexity', 'duplications', 'issues', 'maintainability', 'reliability', 'security', 'size', 'tests']
                        
    def _run(self, metric_name):
        metrics = self.analyze_metrics(metric_name)
        result = ""
        for evaluation in metrics:
            result += f"- {evaluation}\n"
        
        return result
      
    def analyze_metrics(self, metric_name: str=''):
        results = []
        if metric_name in self.metrics:
            with open(f'{self.path_metrics}{metric_name}.json', 'r') as arquivo:
                json_data = json.load(arquivo)
                for componente in json_data['Metrics']:
                    result = self.request_metrics(componente['key'])
                    results.append(result)
            return results
        raise Exception(f"{metric_name} não é uma opção válida: {self.metrics}")
                    
    def request_metrics(self, metric_key):
        response = requests.get(
            f"{self.sonar_url}/api/measures/component?component={self.project_key}&metricKeys={metric_key}",
            headers={"Authorization": f"Bearer {self.sonar_token}"},
        )

        return self.get_value_metric(response.json(), metric_key)
    
    def get_value_metric(self, response, metric_name):
        response = response["component"]["measures"]
        metric_value = response[0]["value"] if len(response) > 0 else 0
        
        return f'{metric_name}: {metric_value}'