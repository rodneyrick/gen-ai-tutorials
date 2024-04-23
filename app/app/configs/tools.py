from enum import Enum

class SonarConfigurations:
    PATH_METRICS = "/workspaces/gen-ai-tutorials/app/tools/sonarqube/metrics"
    SONAR_DIR = "/workspaces/gen-ai-tutorials/app/tools/sonarqube"
    SONAR_SCANNER_PATH = "/workspaces/gen-ai-tutorials/app/tools/sonarqube/sonar-scanner-5.0.1.3006-linux"
    SONAR_SCANNER_DOWNLOAD = "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip?_gl=1*8egwxx*_gcl_au*MTA0NjMwMjU1OS4xNzEyMTY4MTE0*_ga*MjE0NjI4OTI4NC4xNzEyMTY4MTE0*_ga_9JZ0GZ5TC6*MTcxMjMyNjM0MS40LjAuMTcxMjMyNjM0MS42MC4wLjA."
    SONAR_SCANNER_VERSION = "sonar-scanner-5.0.1.3006-linux"

class GitConfigurations:
    REPOS_PATH= "/workspaces/gen-ai-tutorials/app/tmp"
    MAX_COMMITS = 100

class SonarDomains(Enum):
    SONAR_DOMAIN_COMPLEXITY = "complexity.json"
    SONAR_DOMAIN_DUPLICATIONS = "duplications.json"
    SONAR_DOMAIN_ISSUES = "issues.json"
    SONAR_DOMAIN_MAINTAINABILITY = "maintainability.json"
    SONAR_DOMAIN_RELIABILITY = "reliability.json"
    SONAR_DOMAIN_SECURITY = "security.json"
    SONAR_DOMAIN_SIZE = "size.json"
    SONAR_DOMAIN_TESTS = "tests.json"

