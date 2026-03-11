import os
import glob
from concurrent.futures import ThreadPoolExecutor

from celltypeAgent import load_json, write_json
from celltypeAgent.tools.utils import add_log
from celltypeAgent.state.state import SingleCluster, MetaData, ClusterInfo

from celltypeAgent.llm.n1n import N1N_LLM

from celltypeAgent.nodes.paramcollector_node import ParamCollectorNode 
from celltypeAgent.nodes.anno_cluster_node import CelltypeAnnoNode
from celltypeAgent.nodes.audit_ann_node import CelltypeAnnAuditNode
from celltypeAgent.nodes.consensus_node import CelltypeConsensusNode
from celltypeAgent import get_llm_config_value



PARM_COLLECT_MODEL = 'gpt-5.4'
ANNOTATION_MODEL   =  ['gpt-5.4', 'claude-sonnet-4-6']
AUDIT_MODEL        = 'claude-sonnet-4-6'
CONSENSUS_MODEL     = 'claude-sonnet-4-6'
MAX_REFLECT_TIMES   = 5
RELIABILITY_THRESHOLD = 70

class CelltypeAgent:
    def __init__(self, marker_table, outdir, provider= 'n1n'):
        self.llm_config_dict = get_llm_config_value(provider)
        self.marker_table = marker_table
        self.outdir = outdir
        self.metadata_state = MetaData()

        self._initialize_metadata_state()
        self._initialize_client()
        self._initialize_nodes()

        if not os.path.exists(self.metadata_state.get_metadata_val('outdir_ann')):
            os.makedirs(self.metadata_state.get_metadata_val('outdir_ann'))
        
        if not os.path.exists(self.metadata_state.get_metadata_val('outdir_audit')):
            os.makedirs(self.metadata_state.get_metadata_val('outdir_audit'))

    @add_log
    def _initialize_metadata_state(self):
        self.metadata_state.update_matadata('marker_table', self.marker_table)
        self.metadata_state.update_matadata('api', self.llm_config_dict['api'])
        self.metadata_state.update_matadata('base_url', self.llm_config_dict['base_url'])
        self.metadata_state.update_matadata('parm_collect_model', PARM_COLLECT_MODEL)
        self.metadata_state.update_matadata('annotation_model', ANNOTATION_MODEL)
        self.metadata_state.update_matadata('audit_model', AUDIT_MODEL)
        self.metadata_state.update_matadata('consensus_model', CONSENSUS_MODEL)

        self.metadata_state.update_matadata('outdir_ann', f"{self.outdir}/init/")
        self.metadata_state.update_matadata('outdir_audit', f"{self.outdir}/audit/")

        
    @add_log
    def _initialize_client(self):

        self.parm_collect_client = N1N_LLM(
            api_key = self.metadata_state.get_metadata_val('api'),
            model_name = self.metadata_state.get_metadata_val('parm_collect_model'),
            base_url = self.metadata_state.get_metadata_val('base_url')
        )

        self.annotation_clients = [
             N1N_LLM(api_key = self.metadata_state.get_metadata_val('api'), 
                model_name = model_name, base_url = self.metadata_state.get_metadata_val('base_url')) 
             for model_name in self.metadata_state.get_metadata_val('annotation_model')
        ]

        self.audit_client = N1N_LLM(
            api_key = self.metadata_state.get_metadata_val('api'),
            model_name = self.metadata_state.get_metadata_val('audit_model'),
            base_url = self.metadata_state.get_metadata_val('base_url'))
        
        self.consensus_client = N1N_LLM(api_key = self.metadata_state.get_metadata_val('api'),
            model_name = self.metadata_state.get_metadata_val('consensus_model'),
            base_url = self.metadata_state.get_metadata_val('base_url'))

    @add_log
    def _initialize_nodes(self):
        self.pnode = ParamCollectorNode(self.parm_collect_client, self.metadata_state)
    
    
    def _ann_single_cluster(self, cluster_id = 0):
        
        # 初始化
        cluster_state = SingleCluster(cluster_id=cluster_id, 
                                      cluster_genes=self.cluster_gene_state.get_cluster_genes(cluster_id))
        
        
        for llm in self.annotation_clients:
            # 进行初始注释
            model_name = llm.get_model_info()['model']
            cnode = CelltypeAnnoNode(self.metadata_state, cluster_state)
            cnode.set_LLM(llm)
            cnode.prep()
            res_ann = cnode.run()
            cluster_state.update_ann_results(model_name, res_ann)

            # 进行注释评分
            audit_node = CelltypeAnnAuditNode(self.audit_client, self.metadata_state, cluster_state)
            audit_node.prep(model_name)
            res_audio = audit_node.run()
            cluster_state.update_audit_results(model_name, res_audio)

            # 反思修正注释结果
            score = res_audio['reliability_score']
            reflect_times = 0

            while score < RELIABILITY_THRESHOLD:
                reflect_times += 1

                print(f"模型 {model_name} 的注释结果被评为不可靠，正在进行第{reflect_times}次反思修正...")
                
                res_ann = cnode.reflect_ann(res_ann)
                cluster_state.update_ann_results(model_name, res_ann)

                res_audio = audit_node.reflect_audit(res_audio)
                cluster_state.update_audit_results(model_name, res_audio)

                score = res_audio['reliability_score']

                if reflect_times >= MAX_REFLECT_TIMES:
                    print(f"模型 {model_name} 的注释结果经过 {MAX_REFLECT_TIMES} 次反思修正后仍被评为不可靠，停止反思修正。本次注释标记为不可靠。")
                    cell_type = cluster_state.get_celltype(model_name)
                    cell_subtype = cluster_state.get_cell_subtype(model_name)

                    cluster_state.update_cell_subtype(model_name, f'(Unreliable)_{cell_type}')
                    cluster_state.update_cell_subtype(model_name, f'(Unreliable)_{cell_subtype}')
                    break
            
        print('\n\n\n\n')
        print(cluster_state)
        print('\n\n\n\n')


                
    @add_log
    def collect_parms(self):
        self.pnode.prep()
        is_complate, results = self.pnode.run()

        if not is_complate:
            raise Exception("参数收集失败，无法继续执行注释流程")
        
        # update metadata state
        for k, v in results['metadata'].items():
            self.metadata_state.update_matadata(k, v)

        self.cluster_gene_state = ClusterInfo(results['cluster'])







INPUT_DATA = f"{os.path.dirname(os.path.dirname(__file__))}/example_data/deg_all.csv"

runner = CelltypeAgent(INPUT_DATA, 'work2/')

runner.collect_parms()
runner._ann_single_cluster()