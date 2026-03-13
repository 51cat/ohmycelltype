
from ohmycelltype.prompt.prompt import PARAM_COLLECTOR_PROMPT
from ohmycelltype.llm.message import Message
from ohmycelltype.llm.tool import Tool
from ohmycelltype.state.state import MetaData
from ohmycelltype.tools.logger import (
    chat_session_header, chat_user_input, chat_ai_chunk
)

from ohmycelltype.tools.agent_tools import collect_parms
from ohmycelltype.tools.utils import extract_and_validate_json, \
    get_table_context, \
        parse_response,\
            execute_task


class ParamCollectorNode:
    def __init__(self, LLM, state: MetaData) -> None:
        self.llm = LLM
        self.marker_table = state.get_metadata_val('marker_table')
    
    def prep(self):
        self.table_summary = get_table_context(self.marker_table)
    
    def run(self):
        chat_session_header()
        
        tools_input = Tool([collect_parms]).desc
        message_input = Message(system_prompt=PARAM_COLLECTOR_PROMPT.format(tools_desc=tools_input))

        message_input.add_user_message(self.table_summary)
        

        while True:
            console = self.llm._get_console() if hasattr(self.llm, '_get_console') else None
            
            response = self.llm.invoke_stream(message_input)

            final_params = extract_and_validate_json(response)
            
            if final_params:
                break

            message_input.add_ai_message(response)

            user_input = chat_user_input()
            message_input.add_user_message(user_input)
        

        results = parse_response(final_params)
        results.update({'df': self.marker_table})

        res = execute_task(
            collect_parms, results
        )
        return res