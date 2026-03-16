# 📊 细胞聚类自动注释分析报告 (Cluster 2)

## 1. 基本信息与共识结果
> 本部分概述该聚类在多模型分析下的身份认同感及结论可靠性。

* **Cluster ID**: 2
* **主要细胞类型 (Cell Type)**: CD8+ T cells
* **细胞亚型 (Subcelltype)**: CD8+ TEMRA cells
* **共识达成情况**: ✅ 已达成共识 (比例: 0.67)
* **信息熵 (Entropy)**: 0.92 (数值越低一致性越高)
* **可靠性评估**: 均分 88 (模型 openai/gpt-5.4: 85, 模型 z-ai/glm-5: 88, 模型 google/gemini-3.1-pro-preview: 88)

---

## 2. 关键特征基因 (Marker Genes)
> 基于高表达基因列表的生物学功能划分。

| 基因分类 | 标志性基因 | 生物学意义 |
| :--- | :--- | :--- |
| **谱系/定义 Marker** | `CD8A` | 明确支持 CD8+ T 细胞谱系归属，提示细胞具有细胞毒性 |
| **亚型特异 Marker** | `FGFBP2`, `ADGRG1`, `S1PR5` | 三者共同出现是 CD8+ TEMRA 细胞的强力证据 |
| **功能/状态标志** | `GZMA`, `GZMH`, `NKG7`, `CCL5` | 表明该群体处于活跃的细胞毒性效应状态，具备强大的杀伤功能 |

---

## 3. 模型推理核心观点对比
> 展现不同 AI 模型在逻辑推演上的异同点。

### 🤖 openai/gpt-5.4
* **核心定义**: Gamma-delta cytotoxic T cells
* **逻辑**: 该模型主要依据 TRGC2 的表达来推断该细胞群体为 γδT细胞，并认为其具有细胞毒性特征。尽管 CD8A 的存在存在一定争议，但模型认为其支持细胞毒效应表型。

### 🎨 z-ai/glm-5
* **核心定义**: CD8+ Effector Memory T cells (Temra)
* **逻辑**: 该模型利用 CD8A 明确支持了 CD8+ T 细胞谱系，并通过对 FGFBP2、ADGRG1 和 S1PR5 的解释进一步理由该群体为 CD8+ Temra。模型合理推测 TRGC2 的存在并不影响最终的细胞类型判定。

### 🪙 google/gemini-3.1-pro-preview
* **核心定义**: CD8+ TEMRA cells
* **逻辑**: 该模型的推论与 z-ai/glm-5 类似，以 CD8A、FGFBP2、ADGRG1 和 S1PR5 为支撑结论，确认细胞含有高细胞毒性特征。TRGC2 提示了少量 γδ T 细胞信号，但整体表达谱高度契合 CD8+ TEMRA。

---

## 4. 审核意见与最终结论 (Audit Consensus)
> 结合顶级专家审核意见，对组织背景和模型偏倚进行最终校正。

> [!IMPORTANT]
> **最终鉴定结论：CD8+ TEMRA cells + 处于活跃细胞毒性状态**

### 核心判定依据：
1. **基因保真度校核结果**: 所有模型均基于 Marker Gene List 中的基因，没有出现基因幻觉。
2. **结合组织背景对特定 Marker 的重新解读**: 模型虽依据 CD8A 及 TRGC2 的表达有所分歧，但最终确认为 CD8+ T 细胞群体，结合 FGFBP2、ADGRG1 和 S1PR5 的高表达证明其为 TEMRA 亚型。
3. **结论建议**: 建议针对 CD8+ TEMRA 细胞群体的功能进行深入研究，考察其在不同病理情况下的表现和潜在应用。