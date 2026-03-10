import os

from celltypeAgent import load_json, write_json
from celltypeAgent.tools.utils import add_log

from celltypeAgent.llm.n1n import N1N_LLM

from celltypeAgent.nodes.paramcollector_node import ParamCollectorNode 
from celltypeAgent.nodes.anno_cluster_node import CelltypeAnnoNode
from celltypeAgent import get_llm_config_value

OUTDIR = './work/'
BASE_URL, API = get_llm_config_value('n1n')
PARM_COLLECT_MODEL = 'gpt-5.4'
ANNOTATION_MODEL   =  ['gpt-5.4', 'claude-sonnet-4-6', 'MiniMax-M2.5', 'qwen3.5-397b-a17b']

# test data

INPUT_DATA = os.path(f"{os.path.dirname(os.path(__file__))}/example_data/deg_all.csv")

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
        write_json(res, f"{outdir}/{llm_name}__init_ann__{cluster}.json")

        init_ann_single_cluster.logger.info(f'finish: {cluster} - model: {llm_name}')
        

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

    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)

    # 用户关键参数收集
        
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

    for clu in genes_all.keys():
        init_ann_single_cluster(
            llm_ann_collect, 
            clu, 
            genes_all[clu], 
            spec, 
            tissue, 
            language, 
            OUTDIR
            )


if __name__ == '__main__':
    main()