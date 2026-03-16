from ohmycelltype.prompt.prompt import INIT_CELLTYPE
from ohmycelltype.llm.message import Message
from ohmycelltype.state.state import SingleCluster,MetaData
from ohmycelltype.tools.utils import extract_and_validate_json
import json

def validate_keys(data):
    expected_top = {'cluster_name', 'cell_type', 'cell_subtype', 'reasoning'}
    expected_reasoning = {'lineage_determination', 'subtype_refinement', 'functional_state'}
    missing_top = expected_top - set(data.keys())
    missing_sub = []
    if 'reasoning' in data and isinstance(data['reasoning'], dict):
        missing_sub = expected_reasoning - set(data['reasoning'].keys())
    elif 'reasoning' not in missing_top:
        return False, "缺失key：reasoning (格式错误)"
    all_missing = list(missing_top) + [f"reasoning.{k}" for k in missing_sub]
    if not all_missing:
        return True, "pass"
    else:
        return False, f"缺失key：{', '.join(all_missing)}"

class CelltypeAnnoNode:
    def __init__(self,  metadata_state: MetaData , state: SingleCluster) -> None:
        self.cluster = state.cluster_id
        self.gene    = ','.join(state.cluster_genes)

        self.spec    = metadata_state.get_metadata_val('spec')
        self.tissue  = metadata_state.get_metadata_val('tissue')
        self.language = metadata_state.get_metadata_val('language')
    
    def set_LLM(self, LLM):
        self.llm = LLM
        
    def prep(self):
        self.system_prompt = INIT_CELLTYPE.format(
        species=self.spec,
        tissue=self.tissue,
        cluster_id=self.cluster,
        gene_list=self.gene,language= self.language
        )
        self.message_input = Message(system_prompt=self.system_prompt)

    
    def run(self):
        self.message_input = Message(system_prompt=self.system_prompt)
        self.message_input.add_user_message('请开始进行注释任务！务必严格遵守我的要求！')
        response = self.llm.invoke(self.message_input)
        self.message_input.add_ai_message(response)

        res = extract_and_validate_json(response)

        return res

    def reflect_ann(self, expert_response):

        if isinstance(expert_response, dict):
            expert_response = json.dumps(expert_response, ensure_ascii=False, indent=2)

        self.message_input.add_user_message(
            '我询问了教授，他对你的注释结果抱有疑问，以下是教授的反馈：\n\n' + \
                expert_response + \
                '\n\n请你根据教授的反馈重新审视你的注释结果，并进行必要的修改。输出格式务必严格遵守我的要求！'
            )
        response = self.llm.invoke(self.message_input)
        self.message_input.add_ai_message(response)

        res = extract_and_validate_json(response)
        return res

        