from app.tools import ToolSonarAnalysis, ToolSonarScanner, ToolGit, GitFunctionalities
from app.configs import SonarDomains, load_dotenv, should_instrumentation, instrumentor
from app.callbacks import ToollCallbackHanlder
from app.telemetry import ToolsInstruments
import os

load_dotenv()

def tool_sonar_scanner():
    instrumentor.setting_instrumentation_tools(ToolsInstruments.TOOLS_SONAR_SCAN)
    tool_output = ToolSonarScanner().run(tool_input={"project_name": "fastapi-lib-observability",
                                                "token": os.environ['SONAR_TOKEN'],
                                                "url": os.environ['SONAR_HOST']},
                                    callbacks=[ToollCallbackHanlder()])
    return tool_output

def tool_sonar_analysis():
    instrumentor.setting_instrumentation_tools(ToolsInstruments.TOOLS_SONAR_ANALYSIS)
    tool_output = ToolSonarAnalysis().run(tool_input={"project_name": "fastapi-lib-observability",
                                                   "token": os.environ['SONAR_TOKEN'],
                                                   "url": os.environ['SONAR_HOST'],
                                                   "metric_name": SonarDomains.SONAR_DOMAIN_ISSUES},
                                       callbacks=[ToollCallbackHanlder()])
    return tool_output

def tool_git_range_commit():
    instrumentor.setting_instrumentation_tools(ToolsInstruments.TOOLS_GIT)
    tool_output = ToolGit().run(tool_input={"project_name": "rdpy-observability",
                                         "url": "https://github.com/lucasBritoo/rdpy-observability",
                                         "function": GitFunctionalities.GIT_COMMITS_RANGE_ID,
                                         "range_commit": "f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829"},
                             callbacks=[ToollCallbackHanlder()])
    return tool_output

def tool_git_clone():
    instrumentor.setting_instrumentation_tools(ToolsInstruments.TOOLS_GIT)
    tool_output = ToolGit().run(tool_input={"project_name": "rdpy-observability",
                                        "url": "https://github.com/lucasBritoo/rdpy-observability",
                                        "function": GitFunctionalities.GIT_CLONE.value},
                            callbacks=[ToollCallbackHanlder()])
    return tool_output

print(tool_git_clone())