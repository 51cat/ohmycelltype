from typing import Dict, Any
from openai import OpenAI
from celltypeAgent.llm.base import BaseLLM
from celltypeAgent.llm.message import Message

class N1N_LLM(BaseLLM):
    def __init__(self, api_key: str, model_name: str | None = None, base_url = None):

        super().__init__(api_key, model_name, base_url)

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def invoke_stream(self, message_input: Message, **kwargs):

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message_input.message, stream = True)

        full_content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content_piece = chunk.choices[0].delta.content
                print(content_piece, end="", flush=True) 
                full_content += content_piece
                
        return full_content
    
    def invoke(self, message_input: Message, **kwargs):

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message_input.message, stream = False)
        return response.choices[0].message.content


    def get_model_info(self) -> Dict[str, Any]:

        return {
            "provider": "N1N",
            "model": self.model_name,
            "api_base": self.base_url
        }

    def get_default_model(self) -> str:
        return ''