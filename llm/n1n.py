from typing import Dict, Any
from openai import OpenAI
from p8.llm.base import BaseLLM
from p8.llm.message import Message

BASE_URL = 'https://api.n1n.ai/v1'

class N1N_LLM(BaseLLM):
    def __init__(self, api_key: str, model_name: str | None = None, base_url = BASE_URL):

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

def main():

    app = N1N_LLM(
        api_key = 'sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D',
        model_name = 'gemini-3.1-pro-preview',
        base_url = "https://api.n1n.ai/v1"
    )

    system_prompt="你是生信专家，我说数字，你给我介绍这个工具，1： fastqc，2：samtools，3：seurat；规则：每个工具用100个字介绍"


    input =  Message(system_prompt)


    input.add_user_message("1")
    respone = app.invoke_stream(input)
    print(respone)

    input.add_ai_message(respone)
    input.add_user_message('2')

    respone = app.invoke_stream(input)
    print(respone)

    input.add_ai_message(respone)
    input.add_user_message('3')

    respone = app.invoke_stream(input)
    print(respone)

    input.add_ai_message(respone)
    input.add_user_message('你一共介绍了几个工具？')

    respone = app.invoke_stream(input)
    print(respone)

    print(input.message)

    '''
    # 初始化客户端
    client = OpenAI(
        base_url="https://api.n1n.ai/v1",
        api_key='您的 API KEY',
        timeout=120
    )

    # 创建聊天完成
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
    )

    '''

if __name__ == '__main__':
    main()