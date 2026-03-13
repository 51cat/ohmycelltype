from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


@dataclass
class MetaData:
    """metadata的注释状态"""
    metadata:     dict = field(default_factory=dict)

    def update_matadata(self, key, value):
        self.metadata.update({key:value})

    def get_metadata_val(self, key):
        return self.metadata[key]

    def to_dict(self):
        return self.metadata

@dataclass
class ClusterInfo:
    """每个cluster的基因"""
    cluster_gene_all: dict = field(default_factory=dict)

    def get_all_cluster(self):
        return self.cluster_gene_all.keys()
    
    def get_cluster_genes(self, cluster):
        return self.cluster_gene_all[cluster]
    
    def to_dict(self):
        return self.cluster_gene_all

@dataclass
class SingleCluster:
    """单个cluster的注释状态"""

    cluster_id: str = ''
    cluster_genes: List[str] = field(default_factory=list)
    ann_results: dict = field(default_factory=dict)
    audit_results: dict = field(default_factory=dict)
    consensus_results: dict = field(default_factory=dict)
    
    
    # 初次注释结果的操作方法
    def get_celltype(self, model_name):
        return self.ann_results[model_name]['cell_type']

    def get_cell_subtype(self, model_name):
        return self.ann_results[model_name]['cell_subtype']
    
    def update_celltype(self, model_name, celltype):
        self.ann_results[model_name]['cell_type'] = celltype
    
    def update_cell_subtype(self, model_name, cell_subtype):
        self.ann_results[model_name]['cell_subtype'] = cell_subtype   
    
    def get_reasoning(self, model_name, to_str = True):
        if to_str:
            return json.dumps(self.ann_results[model_name]['reasoning'], ensure_ascii=False)
        return self.ann_results[model_name]['reasoning']

    def update_ann_results(self, model_name, res):
        self.ann_results[model_name] = res
    
    def update_audit_results(self, model_name, res):
        self.audit_results[model_name] = res
    
    def updata_consensus_results(self, res):
        self.consensus_results = res

    def ann_to_dict(self):
        return self.ann_results
    
    def audit_to_dict(self):
        return self.audit_results
    
    def consensus_to_dict(self):
        return self.consensus_results