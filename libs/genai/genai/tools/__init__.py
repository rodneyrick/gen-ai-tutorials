import os
from genai.tools.tools_configs import SonarConfigurations, GitConfigurations, SonarDomains

if not os.path.exists(GitConfigurations.REPOS_PATH):
    os.makedirs(GitConfigurations.REPOS_PATH)
    
if not os.path.exists(SonarConfigurations.SONAR_DIR):
    os.makedirs(SonarConfigurations.SONAR_DIR)

from genai.tools.tools_sonar_scanner import ToolSonarScanner
from genai.tools.tools_sonar_analysis import ToolSonarAnalysis
from genai.tools.tools_git import ToolGit, GitFunctionalities
from genai.tools.tools_llm_chat import ToolChatLLM


__all__ = [
    "ToolSonarScanner", 
    "ToolSonarAnalysis", 
    "GitFunctionalities",
    "ToolGit",
    "ToolChatLLM",
    "SonarConfigurations",
    "GitConfigurations",
    "SonarDomains"
]