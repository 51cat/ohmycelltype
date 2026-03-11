import os
import glob
from concurrent.futures import ThreadPoolExecutor

from celltypeAgent import load_json, write_json
from celltypeAgent.tools.utils import add_log
from celltypeAgent.state.state import SingleCluster, MetaData

from celltypeAgent.llm.n1n import N1N_LLM

from celltypeAgent.nodes.paramcollector_node import ParamCollectorNode 
from celltypeAgent.nodes.anno_cluster_node import CelltypeAnnoNode
from celltypeAgent.nodes.audit_ann_node import CelltypeAnnAuditNode
from celltypeAgent import get_llm_config_value

OUTDIR = './work/'
OUTDIR_INIT = f"{OUTDIR}/init/"
OUTDIR_AUDIT = f"{OUTDIR}/audit/"

BASE_URL, API = get_llm_config_value('n1n')
PARM_COLLECT_MODEL = 'gpt-5.4'
ANNOTATION_MODEL   =  ['gpt-5.4', 'claude-sonnet-4-6', 'MiniMax-M2.5', 'qwen3.5-397b-a17b']
AUDIT_MODEL = 'claude-sonnet-4-6'


class CelltypeAgent:
    def __init__(self, marker_table, outdir, provider= 'n1n'):
        self.llm_config_dict = get_llm_config_value(provider)
        self.marker_table = marker_table
        self.outdir = outdir
        self.metadata_state = MetaData()

    def _initialize_metadata_state(self):
        self.metadata_state.update_matadata('api', self.llm_config_dict['api'])
        self.metadata_state.update_matadata('base_url', self.llm_config_dict['base_url'])
        self.metadata_state.update_matadata('parm_collect_model', PARM_COLLECT_MODEL)
        self.metadata_state.update_matadata('annotation_model', ANNOTATION_MODEL)
        self.metadata_state.update_matadata('audit_model', AUDIT_MODEL)

        self.metadata_state.update_matadata('outdir_ann', f"{self.outdir}/init/")
        self.metadata_state.update_matadata('outdir_audit', f"{self.outdir}/audit/")

    def _initialize_nodes(self):
        pass







# test data

INPUT_DATA = f"{os.path.dirname(os.path.dirname(__file__))}/example_data/test.csv"

@add_log
def init_ann_single_cluster(llms, cluster, genes, spec, tissue, language, outdir):
    for llm in llms:
        llm_name = llm.get_model_info()['model']
        init_ann_single_cluster.logger.info(f'start: {cluster} - model: {llm_name}')
        cnode = CelltypeAnnoNode(llm, cluster, genes, tissue, spec)
        cnode.set_language(language)
        cnode.prep()
        res = cnode.run()
        
        res['model'] = llm_name
        res['spec'] = spec
        res['tissue'] = tissue
        res['genes'] = genes
        res['language'] = language
        res['language'] = language
        res['genes'] = ",".join(genes)

        if os.path.exists(f"{OUTDIR_INIT}/{cluster}/") == False:
            os.makedirs(f"{OUTDIR_INIT}/{cluster}/")

        write_json(res, f"{OUTDIR_INIT}/{cluster}/{llm_name}__init_ann__{cluster}.json")

        init_ann_single_cluster.logger.info(f'finish: {cluster} - model: {llm_name}')
        
@add_log
def audit_single_cluster(llm, ann_dict, outdir):
    cluster = ann_dict['cluster_name']
    llm_name = ann_dict['model']
    audit_single_cluster.logger.info(f'start audit: {cluster} - model: {llm_name}')
    audit_node = CelltypeAnnAuditNode(llm, ann_dict)
    audit_node.prep()
    res = audit_node.run()
    ann_dict['audit'] = res

    if os.path.exists(f"{OUTDIR_AUDIT}/{cluster}/") == False:
        os.makedirs(f"{OUTDIR_AUDIT}/{cluster}/")

    write_json(ann_dict, f"{OUTDIR_AUDIT}/{cluster}/{llm_name}__audit_ann__{cluster}.json")
    audit_single_cluster.logger.info(f'finish audit: {cluster} - model: {llm_name}')

@add_log
def main():

    llm_parm_collect = [N1N_LLM(
            api_key = API,
            model_name = PARM_COLLECT_MODEL,
            base_url = BASE_URL
    ),]

    llm_ann_collect = [
        N1N_LLM(api_key = API, model_name = model_name, base_url = BASE_URL) 
        for model_name in ANNOTATION_MODEL
    ]

    llm_audit = N1N_LLM(api_key = API, model_name = AUDIT_MODEL, base_url = BASE_URL)

    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)

    # 用户关键参数收集
    if os.path.exists(f"{OUTDIR}/args.json"):
        gene_dict = load_json(f"{OUTDIR}/args.json")
        main.logger.info(f"参数加载成功！")
    else:   
        pcnode = ParamCollectorNode(llm_parm_collect[0], INPUT_DATA)
        pcnode.prep()
        gene_dict = pcnode.run()[1]

    meta = gene_dict['metadata']

    spec =  meta['spec']
    tissue = meta['tissue']
    language = meta['language']

    genes_all = gene_dict['cluster']

    write_json(gene_dict, f"{OUTDIR}/args.json")
    main.logger.info(f"Start!")

    
    
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(init_ann_single_cluster, 
                     [llm_ann_collect] * len(genes_all), 
                     list(genes_all.keys()), 
                     [genes_all[clu] for clu in genes_all.keys()], 
                     [spec] * len(genes_all), 
                     [tissue] * len(genes_all), 
                     [language] * len(genes_all), 
                     [OUTDIR] * len(genes_all))
    
    
    all_init_res = glob.glob(f"{OUTDIR_INIT}/*/*json")
    all_init_res = [f for f in all_init_res if 'json' in f]
    all_init_res_dict = [load_json(f) for f in all_init_res]
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(audit_single_cluster, 
                     [llm_audit] * len(all_init_res_dict), 
                     all_init_res_dict, 
                     [OUTDIR] * len(all_init_res_dict))

if __name__ == '__main__':
    main()