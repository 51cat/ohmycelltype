# 📊 细胞聚类自动注释分析报告 (Cluster 20)

## 1. 基本信息与共识结果
> 本部分概述该聚类在多模型分析下的身份认同感及结论可靠性。

* **Cluster ID**: 20
* **主要细胞类型 (Cell Type)**: Dendritic cells
* **细胞亚型 (Subcelltype)**: Conventional dendritic cells (cDC)
* **共识达成情况**: ✅ 已达成共识 (比例: 0.67)
* **信息熵 (Entropy)**: 0.92
* **可靠性评估**: 均分 74 (模型 openai/gpt-5.4: 72, 模型 google/gemini-3.1-pro-preview: 82)

---

## 2. 关键特征基因 (Marker Genes)
> 基于高表达基因列表的生物学功能划分。

| 基因分类 | 标志性基因 | 生物学意义 |
| :--- | :--- | :--- |
| **谱系/定义 Marker** | `HLA-DQA1`, `HLA-DPA1`, `HLA-DRB5` | 高表达的 MHC-II 类分子基因是专业抗原呈递细胞（APC）的典型特征，表明该 cluster 具有髓系来源。 |
| **亚型特异 Marker** | `NAPSB`, `IL13RA1` | 虽然在 cDC 亚群中有表达，但特异性不足以单独区分亚型。 |
| **功能/状态标志** | `GSN`, `HLA-DQA2` | 显示该细胞处于活跃的抗原呈递功能状态，参与细胞重塑和抗原加工。 |

---

## 3. 模型推理核心观点对比
> 展现不同 AI 模型在逻辑推演上的异同点。

### 🤖 openai/gpt-5.4
* **核心定义**: Myeloid cells
* **逻辑**: 该模型视为髓系抗原呈递细胞，基于高表达的多种 MHC-II 相关基因进行推理，支持其为传统树突状细胞（cDC2）的身份，结合 PBMC 的组织背景，得出结论具有合理性。

### 🎨 google/gemini-3.1-pro-preview
* **核心定义**: Conventional dendritic cell
* **逻辑**: 该模型强调多种 MHC-II 类分子的高表达，同时结合 GSN 和 IL13RA1 的髓系特征，表明该 cluster 符合常规树突状细胞的转录组特征，认为该细胞具备强烈的抗原呈递能力。

---

## 4. 审核意见与最终结论 (Audit Consensus)
> 结合顶级专家审核意见，对组织背景和模型偏倚进行最终校正。

> [!IMPORTANT]
> **最终鉴定结论：Conventional dendritic cells (cDC) + 处于活跃抗原呈递状态**

### 核心判定依据：
1. **基因保真度校核结果**: 所有模型均未发现 gene hallucination，使用的基因均来自 Marker Gene List，保证了结果的可信性。
2. **结合组织背景对特定 Marker 的重新解读**: 尽管 MHC-II 类分子同样高表达于其它细胞类型，但结合 NAPSB 等 marker 仍指向此 cluster 为髓系来源的传统树突状细胞。
3. **结论建议**: 建议后续研究进一步结合细胞表面特征以明确 cDC 的亚群，特别是关键 marker CLEC9A/CD1C 的活跃性检测。