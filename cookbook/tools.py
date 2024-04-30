from genai.tools import ToolSonarAnalysis, ToolSonarScanner, ToolGit, GitFunctionalities, ToolChatLLM
from genai.tools.tools_configs import SonarDomains
from genai_core.logging import logging
from genai_core.prompts import create_prompt_list
from textwrap import dedent
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

logger = logging.getLogger()

async def tool_sonar_scanner():
    tool_output = await ToolSonarScanner().run(tool_input={
        "project_name": "gen-ai-tutorials",
        "token": os.environ['SONAR_TOKEN'],
        "url": os.environ['SONAR_HOST'],
    })
    
    logger.debug(tool_output)

async def tool_sonar_analysis():
    tool_output = await ToolSonarAnalysis().run(tool_input={
        "project_name": "rdpy-observability",
        "token": os.environ['SONAR_TOKEN'],
        "url": os.environ['SONAR_HOST'],
        "domain": SonarDomains.SONAR_DOMAIN_ISSUES
    })
    
    logger.debug(tool_output)

async def tool_git_range_commit():
    tool_output = await ToolGit().run(tool_input={
        "project_name": "rdpy-observability",
        "url": "https://github.com/lucasBritoo/rdpy-observability",
        "function": GitFunctionalities.GIT_COMMITS_RANGE_ID,
        "range_commit": "f2481149d9585dd956541cef1881be7f9ab81dbd..cef16a9f64d836a3221a344ca7d571644280d829"
    })
    
    logger.debug(tool_output)

async def tool_git_clone():
    tool_output = await ToolGit().run(tool_input={
        "project_name": "gen-ai-tutorials",
        "url": "https://github.com/rodneyrick/gen-ai-tutorials",
        "function": GitFunctionalities.GIT_CLONE
    })
    
    logger.debug(tool_output)

async def tool_llm_chat():
    prompt = create_prompt_list([
        {
            "role": "user", 
            "content": dedent("""
                Tell me a joke!!
            """)
        }
    ])
    
    logger.debug("Create chat")
    tool_output = await ToolChatLLM().run(tool_input={"model": os.environ['OPENAI_MODEL_NAME'], 
                                             "api_key": os.environ['OPENAI_API_KEY'],
                                             "api_base": os.environ['OPENAI_BASE_URL'],
                                             "prompt": prompt,
                                             "streaming": False})
        
    logger.debug(tool_output)
    
asyncio.run(tool_sonar_scanner())