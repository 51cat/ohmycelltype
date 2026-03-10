from celltypeAgent.prompt.prompt import INIT_CELLTYPE
from celltypeAgent.llm.n1n import N1N_LLM
from celltypeAgent.llm.message import Message
from celltypeAgent.tools.utils import extract_and_validate_json

class CelltypeAnnoNode:
    def __init__(self, LLM, cluster, genes, spec, tissue) -> None:
        self.llm = LLM
        self.cluster = cluster
        self.gene = ','.join(genes)
        self.spec = spec
        self.tissue = tissue
    
    def set_language(self, language):
        self.language = language

    def prep(self):
        self.system_prompt = INIT_CELLTYPE.format(
        species=self.spec,
        tissue=self.tissue,
        cluster_id=self.cluster,
        gene_list=self.gene,language= self.language
        )

    def run(self):
        message_input = Message(system_prompt=self.system_prompt)
        message_input.add_user_message('请开始进行注释任务！务必严格遵守我的要求！')
        response = self.llm.invoke(message_input)
        res = extract_and_validate_json(response)
        return res
        


def main():

    llm_grok = N1N_LLM(
        api_key = 'sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D',
        model_name = 'claude-sonnet-4-6',
        base_url = "https://api.n1n.ai/v1"
    )
    llm_gpt = N1N_LLM(
        api_key = 'sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D',
        model_name = 'gpt-5.4',
        base_url = "https://api.n1n.ai/v1"
    )
    cluster_name = "Cluster_7"
    markers = ['TRAJ61', 'CTB-91J4.1', 'ZNF683', 'TRAV23DV6', 'LINC00384', 'PROK2', 'B3GAT1', 'GZMH', 'RP11-9M16.2', 'RP11-305L7.3']
    context = "Peripheral Blood Mononuclear Cells (PBMC)"

    pcnode = CelltypeAnnoNode(llm_grok,cluster_name,markers,'human',context)
    pcnode.prep()
    a = pcnode.run()

    pcnode = CelltypeAnnoNode(llm_gpt,cluster_name,markers,'human',context)
    pcnode.prep()
    a = pcnode.run()
    

    

if __name__ == '__main__':
    main()


        