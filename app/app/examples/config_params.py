from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import parse_obj_as
from app.prompts import create_prompt_list, PromptsTemplateModel, PromptTemplateModel

from typing import List

def run():
    prompt_text = """
    You are a Git expert.
    {test}
    """
    prompt_text1 = """
    You are a Git expert.
    """

    s = parse_obj_as(List[PromptTemplateModel],[{
        "role" : "system", 
        "content" : PromptTemplate.from_template(prompt_text),
        "parameters": {'test': 1}
    },
    {
        "role" : "system", 
        "content" : PromptTemplate.from_template(prompt_text1)
    }
    ])
    s = PromptsTemplateModel(prompts=s)

    print(s.to_list())
