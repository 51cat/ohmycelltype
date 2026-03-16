import time
from typing import Dict, Any
from openai import OpenAI
from ohmycelltype.llm.base import BaseLLM
from ohmycelltype.llm.message import Message
from ohmycelltype.tools.logger import (
    console, print_stream_header, print_stream_footer, 
    wait_animation, is_valid_response, log_retry, log_error
)


class OpenRouter_LLM(BaseLLM):
    def __init__(self, api_key: str, model_name: str | None = None, base_url: str | None = None):

        super().__init__(api_key, model_name, base_url)

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def invoke_stream(self, message_input: Message, **kwargs):

        print_stream_header(self.model_name)

        for attempt in range(1, self.max_retry + 1):
            try:
                with wait_animation():
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=message_input.message, stream=True)

                    full_content = ""
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_content += chunk.choices[0].delta.content
                
                if is_valid_response(full_content):
                    console.print(full_content, style="white")
                    print_stream_footer()
                    return full_content
                else:
                    raise ValueError("无效响应")
                    
            except Exception as e:
                if attempt < self.max_retry:
                    delay = 2 ** (attempt - 1)
                    log_retry(attempt + 1, delay, type(e).__name__)
                    time.sleep(delay)
                else:
                    log_error(f"重试 {self.max_retry} 次后仍失败")
                    print_stream_footer()
                    raise
    
    def invoke(self, message_input: Message, **kwargs):

        for attempt in range(1, self.max_retry + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=message_input.message, stream=False)
                
                content = response.choices[0].message.content
                
                if is_valid_response(content):
                    return content
                else:
                    raise ValueError("无效响应")
                    
            except Exception as e:
                if attempt < self.max_retry:
                    delay = 2 ** (attempt - 1)
                    log_retry(attempt + 1, delay, type(e).__name__)
                    time.sleep(delay)
                else:
                    log_error(f"重试 {self.max_retry} 次后仍失败")
                    raise


    def get_model_info(self) -> Dict[str, Any]:

        return {
            "provider": "OpenRouter",
            "model": self.model_name,
            "api_base": self.base_url
        }

    def get_default_model(self) -> str:
        return "openai/gpt-4o-mini"
