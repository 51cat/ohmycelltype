from ohmycelltype.prompt.prompt import CLUSTER_REPORT_PROMPT
from ohmycelltype.llm.message import Message
from ohmycelltype.state.state import SingleCluster, MetaData
from ohmycelltype.tools.utils import clean_markdown_format
import json



class CelltypeReportNode:
    def __init__(self, LLM, state: SingleCluster) -> None:
        self.llm = LLM
        self.state = state

    def prep(self):
        
        self.system_prompt = CLUSTER_REPORT_PROMPT.format(
            ann_results = json.dumps(self.state.ann_to_dict(), ensure_ascii=False),
            audit_results = json.dumps(self.state.audit_to_dict(), ensure_ascii=False),
            consensus_results = json.dumps(self.state.consensus_to_dict(), ensure_ascii=False)
        )
        self.message_input = Message(system_prompt=self.system_prompt)
        
    def run(self):
        self.message_input.add_user_message('请开始进行任务！务必严格遵守我的要求！')
        response = self.llm.invoke(self.message_input)
        self.message_input.add_ai_message(response)

        res = clean_markdown_format(response)
        return res
