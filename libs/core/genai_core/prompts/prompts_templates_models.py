from langchain.pydantic_v1 import BaseModel, Field, parse_obj_as
from langchain.prompts import PromptTemplate
from typing  import List, Optional
from genai_core.telemetry import instrumented_trace, TraceInstruments

class PromptTemplateModel(BaseModel):
    role: str = Field(None, description="Prompet Typed used to instruction the content information")
    content: str = Field(None, description="Content of Template prompet")
    parameters: Optional[dict] = Field({}, description="Extra parameters")

    @instrumented_trace(span_name="Format Template Prompt", type=TraceInstruments.INSTRUMENTS_EVENT)
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
    
@instrumented_trace(span_name="Create Prompt List", span_parameters=False)
def create_prompt_list(prompts: List[dict] = {}):
    if not prompts:
        raise ValueError('Variable `prompts` is empty!')
    return PromptsTemplateModel(
        prompts = parse_obj_as(List[PromptTemplateModel], prompts)
    ).to_list()