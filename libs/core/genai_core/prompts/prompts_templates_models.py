from langchain.pydantic_v1 import BaseModel, Field, parse_obj_as
from langchain.prompts import PromptTemplate
from typing  import List, Optional

class PromptTemplateModel(BaseModel):
    role: str = Field(None, description="Prompet Typed used to instruction the content information")
    content: str = Field(None, description="Content of Template prompet")
    parameters: Optional[dict] = Field({}, description="Extra parameters")

    def to_dict(self):
        
        ctt = PromptTemplate.from_template(self.content)

        if self.parameters:
            ctt = ctt.format(**self.parameters)
        return {
            "role": self.role,
            "content": ctt.format()
        }

class PromptsTemplateModel(BaseModel):
    prompts: List[PromptTemplateModel]

    def to_list(self):
        return [p.to_dict() for p in self.prompts]
    

def create_prompt_list(prompts: List[dict] = {}):
    if not prompts:
        raise ValueError('Variable `prompts` is empty!')
    return PromptsTemplateModel(
        prompts = parse_obj_as(List[PromptTemplateModel], prompts)
    ).to_list()