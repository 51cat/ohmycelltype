from ohmycelltype.prompt.prompt import AUDIT_PROMPT
from ohmycelltype.llm.message import Message
from ohmycelltype.state.state import SingleCluster, MetaData
from ohmycelltype.tools.utils import extract_and_validate_json
import json

class CelltypeAnnAuditNode:
    def __init__(self, LLM, metadata_state: MetaData, state: SingleCluster) -> None:
        self.llm = LLM
        self.state = state
        self.metadata_state = metadata_state

    def prep(self, ann_model_name):
        self.cell_type = self.state.get_celltype(ann_model_name)
        self.cell_subtype = self.state.get_cell_subtype(ann_model_name)
        self.reasoning = self.state.get_reasoning(ann_model_name)
        
        self.system_prompt = AUDIT_PROMPT.format(
            species = self.metadata_state.get_metadata_val('spec'),
            tissue  = self.metadata_state.get_metadata_val('tissue'),
            model_name= ann_model_name,
            genes=','.join(self.state.cluster_genes),
            language=self.metadata_state.get_metadata_val('language'),
            cell_type=self.cell_type,
            cell_subtype=self.cell_subtype,
            reasoning=self.reasoning
        )
        self.message_input = Message(system_prompt=self.system_prompt)
        
    def run(self):
        self.message_input.add_user_message('请开始进行注释结果评价任务！务必严格遵守我的要求！')
        response = self.llm.invoke(self.message_input)
        self.message_input.add_ai_message(response)

        res = extract_and_validate_json(response)
        return res

    def reflect_audit(self, response):
        if isinstance(response, dict):
            response = json.dumps(response, ensure_ascii=False, indent=2)
        
        self.message_input.add_user_message('我根据你的评价结果进行了反思修正，以下是我的修正结果：\n\n' + \
                                            response + \
                                            '\n\n 请你再次进行评价！, 输出格式务必还要坚持我的要求！')
        
        response = self.llm.invoke(self.message_input)
        self.message_input.add_ai_message(response)
        res = extract_and_validate_json(response)
        return res
