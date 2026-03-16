import os
import glob
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from ohmycelltype import load_json, write_json
from ohmycelltype.tools.utils import add_log
from ohmycelltype.tools.logger import (
    log_info, log_warning, log_success, 
    display_annotation_table, display_section_header
)
from ohmycelltype.state.state import SingleCluster, MetaData, ClusterInfo

from ohmycelltype.llm.n1n import N1N_LLM
from ohmycelltype.llm.openrouter import OpenRouter_LLM

from ohmycelltype.nodes.paramcollector_node import ParamCollectorNode 
from ohmycelltype.nodes.anno_cluster_node import CelltypeAnnoNode
from ohmycelltype.nodes.audit_ann_node import CelltypeAnnAuditNode
from ohmycelltype.nodes.consensus_node import CelltypeConsensusNode
from ohmycelltype.nodes.report_node import CelltypeReportNode
from ohmycelltype import get_llm_config_value
from ohmycelltype.tools.render import HTMLRenderer


class CelltypeWorkflow:
    def __init__(self, marker_table, outdir, provider= 'openrouter'):
        self.llm_config_dict = get_llm_config_value(provider)
        self.provider = provider
        self.marker_table = marker_table
        self.outdir = outdir
        self.metadata_state = MetaData()

        self._initialize_metadata_state()
        self._initialize_client()
        self._initialize_nodes()
        

    def _initialize_metadata_state(self):
        self.metadata_state.update_matadata('marker_table', self.marker_table)
        self.metadata_state.update_matadata('api', self.llm_config_dict['api'])
        self.metadata_state.update_matadata('base_url', self.llm_config_dict['base_url'])
        self.metadata_state.update_matadata('parm_collect_model', self.llm_config_dict['parm_collect_model'])
        self.metadata_state.update_matadata('annotation_model', self.llm_config_dict['annotation_model'])
        self.metadata_state.update_matadata('audit_model', self.llm_config_dict['audit_model'])
        self.metadata_state.update_matadata('consensus_model', self.llm_config_dict['consensus_model'])
        self.metadata_state.update_matadata('report_model',  self.llm_config_dict['report_model'])
        self.metadata_state.update_matadata('max_retry',  self.llm_config_dict['max_retry'])
        self.metadata_state.update_matadata('max_reflect_times',  self.llm_config_dict['max_reflect_times'])
        self.metadata_state.update_matadata('reliability_threshold',  self.llm_config_dict['reliability_threshold'])

        self.metadata_state.update_matadata('outdir', f"{self.outdir}/")

        log_info("Metadata state initialized with configuration values", highlight=True)
        log_info("Param collect model: " + self.metadata_state.get_metadata_val('parm_collect_model'))
        log_info("Annotation models: " + ", ".join(self.metadata_state.get_metadata_val('annotation_model')))
        log_info("Audit model: " + self.metadata_state.get_metadata_val('audit_model'))
        log_info("Consensus model: " + self.metadata_state.get_metadata_val('consensus_model'))
        log_info("Report model: " + self.metadata_state.get_metadata_val('report_model'))
        log_info("Reliability threshold: " + str(self.metadata_state.get_metadata_val('reliability_threshold')))
        log_info("Max retry: " + str(self.metadata_state.get_metadata_val('max_retry')))
        log_info("Max reflect times: " + str(self.metadata_state.get_metadata_val('max_reflect_times')))
        
    
    def _initialize_client(self):

        if self.provider == 'n1n':
            self.client_class = N1N_LLM
        elif self.provider == 'openrouter':
            self.client_class = OpenRouter_LLM
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        max_retry = self.metadata_state.get_metadata_val('max_retry')
        api = self.metadata_state.get_metadata_val('api')
        base_url = self.metadata_state.get_metadata_val('base_url')

        self.parm_collect_client = self.client_class(
            api_key = api,
            model_name = self.metadata_state.get_metadata_val('parm_collect_model'),
            base_url = self.metadata_state.get_metadata_val('base_url')
        )

        self.parm_collect_client.set_max_retry(max_retry)

        self.annotation_clients = [
             self.client_class(api_key = api, 
                model_name = model_name, base_url = base_url) 
             for model_name in self.metadata_state.get_metadata_val('annotation_model')
        ]

        for client in self.annotation_clients:
            client.set_max_retry(max_retry)

        
        self.audit_client = self.client_class(
            api_key = api,
            model_name = self.metadata_state.get_metadata_val('audit_model'),
            base_url = base_url)
        self.audit_client.set_max_retry(max_retry)

        
        self.consensus_client = self.client_class(api_key = api,
            model_name = self.metadata_state.get_metadata_val('consensus_model'),
            base_url = base_url)
        self.consensus_client.set_max_retry(max_retry)
        
        self.report_client = self.client_class(api_key = api,
            model_name = self.metadata_state.get_metadata_val('report_model'),
            base_url = base_url)
        self.report_client.set_max_retry(max_retry)


    @add_log
    def _initialize_nodes(self):
        self.pnode = ParamCollectorNode(self.parm_collect_client, self.metadata_state)
    
    @add_log
    def _ann_single_cluster(self, cluster_id = 0):
        
        display_section_header(f"Cluster {cluster_id} 注释流程", "🔬")
        
        cluster_state = SingleCluster(cluster_id=cluster_id, 
                                      cluster_genes=self.cluster_gene_state.get_cluster_genes(cluster_id))
        
        annotation_results = []

        reliability_threshold = self.metadata_state.get_metadata_val('reliability_threshold')
        max_reflect_times = self.metadata_state.get_metadata_val('max_reflect_times')
        
        for llm in self.annotation_clients:
            model_name = llm.get_model_info()['model']
            log_info(f"开始 [bold]{model_name}[/bold] 模型注释 cluster 「{cluster_id}」...", highlight=True)
            
            cnode = CelltypeAnnoNode(self.metadata_state, cluster_state)
            cnode.set_LLM(llm)
            cnode.prep()
            res_ann = cnode.run()
            cluster_state.update_ann_results(model_name, res_ann)

            audit_node = CelltypeAnnAuditNode(self.audit_client, self.metadata_state, cluster_state)
            audit_node.prep(model_name)
            res_audio = audit_node.run()
            cluster_state.update_audit_results(model_name, res_audio)

            score = res_audio['reliability_score']
            reflect_times = 0

            while score < reliability_threshold:
                reflect_times += 1

                log_warning(f"模型 {model_name} 不可靠，第 {reflect_times} 次反思修正，cluster 「{cluster_id}」...")
                
                res_ann = cnode.reflect_ann(res_ann)
                cluster_state.update_ann_results(model_name, res_ann)

                res_audio = audit_node.reflect_audit(res_audio)
                cluster_state.update_audit_results(model_name, res_audio)

                score = res_audio['reliability_score']

                if reflect_times >= max_reflect_times:
                    log_warning(f"模型 {model_name} 经过 {max_reflect_times} 次反思仍不可靠，cluster 「{cluster_id}」标记为 Unreliable，停止反思")
                    cell_type = cluster_state.get_celltype(model_name)
                    cell_subtype = cluster_state.get_cell_subtype(model_name)

                    cluster_state.update_cell_subtype(model_name, f'(Unreliable)_{cell_type}')
                    cluster_state.update_cell_subtype(model_name, f'(Unreliable)_{cell_subtype}')
                    break

            log_success(f"模型 {model_name} 完成 cluster 「{cluster_id}」，可靠性评分: {score}")
            
            annotation_results.append({
                "model": model_name,
                "cell_type": cluster_state.get_celltype(model_name),
                "cell_subtype": cluster_state.get_cell_subtype(model_name),
                "score": score
            })
        
        display_annotation_table(annotation_results, f"Cluster {cluster_id} 注释结果")
        
        log_info(f"开始共识检验...", highlight=True)
        
        connode = CelltypeConsensusNode(self.consensus_client, self.metadata_state, cluster_state)
        connode.prep()
        res_con = connode.run()
        cluster_state.updata_consensus_results(res_con)

        log_success(f"共识检验完成")

        log_info(f"生成报告...", highlight=True)
        
        rnode = CelltypeReportNode(self.report_client, cluster_state)
        rnode.prep()
        res_report = rnode.run()

        outdir = self.metadata_state.get_metadata_val('outdir')
        log_outdir = f"{outdir}/log/{cluster_id}/"
        self.report_dir = f"{outdir}/report/"

        if not os.path.exists(log_outdir):
            os.makedirs(log_outdir, exist_ok=True)
        
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir, exist_ok=True)
        
        write_json(cluster_state.ann_to_dict(), f"{log_outdir}/ann_results.json")
        write_json(cluster_state.audit_to_dict(), f"{log_outdir}/audit_results.json")
        write_json(cluster_state.consensus_to_dict(), f"{log_outdir}/consensus_results.json")
        write_json(MetaData.to_dict(self.metadata_state), f"{log_outdir}/metadata.json")

        with open(f"{self.report_dir}/report_{cluster_id}.md", 'w', encoding='utf-8') as f:
            f.write(res_report)
        
        final_df = pd.DataFrame({'cluster_id': [cluster_id],
                                 'celltype':[cluster_state.consensus_to_dict()['celltype']],
                                 'subtype': [cluster_state.consensus_to_dict()['subcelltype']]})
        final_df.to_csv(f"{self.report_dir}/final_annotation_{cluster_id}.csv", index=False)
        log_success(f"Cluster {cluster_id} 处理完成，结果已保存")
        
                
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
    
    def multi_cluster_annotation(self):
        #cluster_ids = self.cluster_gene_state.get_all_cluster()

        #for cluster_id in cluster_ids:
        #    self._ann_single_cluster(cluster_id)
        cluster_ids = self.cluster_gene_state.get_all_cluster()
        
        
        with ThreadPoolExecutor(max_workers=min(8, len(cluster_ids))) as executor:
            executor.map(self._ann_single_cluster, cluster_ids)
        
        results_file =glob.glob(f"{self.report_dir}/final_annotation_*.csv")
        all_results = []
        for file in results_file:
            df = pd.read_csv(file)
            all_results.append(df)
        final_results_df = pd.concat(all_results, ignore_index=True)
        final_results_df.to_csv(f"{self.report_dir}/final_annotation_all_clusters.csv", index=False)

        # report dict
        all_report = glob.glob(f"{self.report_dir}/report_*.md")
        all_report_dict = {}
        for file in all_report:
            cluster_id = os.path.basename(file).split('_')[1].split('.')[0]
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_report_dict[cluster_id] = content

        log_success(f"所有 Cluster 注释完成，最终结果已保存")

        render = HTMLRenderer(final_results_df, all_report_dict)
        render.save_to_file(f"{self.report_dir}/final_report.html")
