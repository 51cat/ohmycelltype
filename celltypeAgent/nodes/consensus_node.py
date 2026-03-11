from celltypeAgent.prompt.prompt import CONSENSUS_ANALYSIS_PROMPT
from celltypeAgent.llm.message import Message
from celltypeAgent.state.state import SingleCluster, MetaData
from celltypeAgent.tools.utils import extract_and_validate_json
import json


class CelltypeConsensusNode:
    def __init__(self, LLM, metadata_state: MetaData, state: SingleCluster) -> None:
        self.llm = LLM
        self.state = state
        self.metadata_state = metadata_state

    def prep(self):
        
        self.system_prompt = CONSENSUS_ANALYSIS_PROMPT.format(
            species = self.metadata_state.get_metadata_val('spec'),
            tissue  = self.metadata_state.get_metadata_val('tissue'),
            cluster_id = self.state.cluster_id,
            ann_results = json.dump(self.state.ann_to_dict(), ensure_ascii=False),
            audit_results = json.dump(self.state.audit_to_dict(), ensure_ascii=False),
            language=self.metadata_state.get_metadata_val('language')
        )
        self.message_input = Message(system_prompt=self.system_prompt)
        
    def run(self):
        self.message_input.add_user_message('请开始进行任务！务必严格遵守我的要求！')
        response = self.llm.invoke(self.message_input)
        self.message_input.add_ai_message(response)

        res = extract_and_validate_json(response)
        return res
