# CelltypeAgent

基于多智能体协作的细胞类型自动注释系统，用于单细胞 RNA 测序数据的细胞类型注释。

## 功能特性

- **多模型并行注释** — GPT、Claude、Qwen、DeepSeek 等模型同时注释
- **共识机制** — 智能聚合多模型预测结果
- **自动审核** — 检测基因幻觉与生物学合理性
- **自我反思** — 最多 5 轮迭代修正低质量注释
- **交互式配置** — 对话式参数收集
- **详细报告** — 输出完整推理链的 Markdown 分析报告

## 安装

```bash
git clone https://github.com/your-repo/CelltypeAgent.git
cd CelltypeAgent
pip install -e .
```

## 配置

编辑 `celltypeAgent/config.json`：

```json
{
    "n1n": {
        "base_url": "https://api.n1n.ai/v1",
        "api": "your-api-key-here"
    }
}
```

## 使用

```bash
# 注释
celltype-agent annotate your_marker_genes.csv -o ./results

# 查看版本
celltype-agent version
```

## 输入格式

CSV 文件应包含差异表达分析结果：

| cluster | gene | p_val_adj | avg_log2FC |
|---------|------|-----------|------------|
| 0 | CD3D | 1.2e-50 | 2.3 |
| 0 | CD3E | 3.4e-45 | 1.9 |
| 1 | CD79A | 5.6e-60 | 3.1 |

交互式参数收集器会帮助映射列名。

## 输出结果

```
results/
├── report/
│   └── report_0.md              # 分析报告
└── log/
    └── 0/
        ├── ann_results.json     # 原始注释
        ├── audit_results.json   # 审核结果
        ├── consensus_results.json # 共识结果
        └── metadata.json        # 运行元数据
```

## 工作流程

```
参数收集 → 多模型并行注释 → 审核评分 → 反思修正(若评分<70) → 共识整合 → 生成报告
```

## 项目结构

```
celltypeAgent/
├── llm/           # LLM 提供商实现
├── nodes/         # 工作流节点
├── state/         # 状态管理
├── prompt/        # 提示模板
├── tools/         # 工具函数
├── cli.py         # CLI 入口
└── workflow.py    # 主工作流
```

## 依赖

- openai
- pandas
- requests
- rich>=13.0.0
- click>=8.0.0

## 开发状态

| 状态 | 功能 |
|:----:|------|
| ✅ | LLM 抽象层 |
| ✅ | 多模型并行注释 |
| ✅ | 基因幻觉检测 |
| ✅ | 共识引擎 |
| ✅ | 自我反思机制 |
| ✅ | 交互式参数收集 |
| ✅ | Markdown 报告生成 |
| 🚧 | 多 cluster 并行处理 |
| 🚧 | 单元测试 |
| 📋 | Web 界面 |
| 📋 | 结果可视化 |
| 📋 | 更多 LLM 提供商 |

## 许可证

MIT License
