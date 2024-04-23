from langchain_openai import ChatOpenAI
from app.callbacks import ToollCallbackHanlder

def create_chat(model, temperature, openai_api_base, openai_api_key):
    chat = ChatOpenAI(openai_api_base=openai_api_base,
                      openai_api_key=openai_api_key,
                      streaming=False, 
                      model=model,
                      temperature=temperature)
    
    return chat