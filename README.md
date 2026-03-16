# ohmycelltype

一个简单易用，基于多大模型协作的细胞类型自动注释系统，用于单细胞 RNA 测序数据的细胞类型注释。

## 功能特性

### 核心功能

- **多模型并行注释** — GPT、Claude、Qwen、DeepSeek、GLM 等模型同时注释，提高注释准确性
- **共识机制** — 智能聚合多模型预测结果，计算信息熵和一致性比例
- **自动审核** — 检测基因幻觉（Gene Hallucination）与生物学合理性
- **自我反思** — 最多 5 轮迭代修正低质量注释（评分低于阈值时自动触发）
- **交互式配置** — 对话式参数收集，智能识别数据列名
- **详细报告** — 输出完整推理链的 Markdown 分析报告
- **HTML 可视化** — 生成精美的交互式 HTML 报告页面

### 技术亮点

- 支持多种 LLM 提供商（OpenRouter、N1N 等）
- 基于 OpenAI SDK 的统一 API 接口
- 并行处理多个 Cluster 提高效率
- 完整的错误处理和重试机制
- Rich 终端美化输出

## 安装

### 从源码安装

```bash
git clone https://github.com/your-repo/ohmycelltype.git
cd ohmycelltype
pip install -e .
```

### 依赖项

```
openai>=1.0.0
pandas>=1.0.0
requests>=2.28.0
rich>=13.0.0
click>=8.0.0
markdown>=3.0.0
```

## 快速开始

### 1. 初始化配置

```bash
# 初始化配置文件（创建 ~/.ohmycelltype.json）
ohmycelltype init-config

# 设置 API Key
ohmycelltype set-api
```

### 2. 运行注释

```bash
# 执行细胞类型注释
ohmycelltype annotate your_marker_genes.csv -o ./results

# 指定 API 提供商
ohmycelltype annotate your_marker_genes.csv -o ./results -p openrouter
```

### 3. 查看结果

```bash
# 查看配置
ohmycelltype show

# 查看版本
ohmycelltype version
```

## 配置说明

### 配置文件位置

配置文件位于 `~/.ohmycelltype.json`

### 完整配置示例

```json
{
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api": "your-api-key-here",
        "parm_collect_model": "openai/gpt-4o-mini",
        "report_model": "openai/gpt-4o-mini",
        "annotation_model": [
            "openai/gpt-4o-mini",
            "google/gemini-2.5-flash-lite",
            "z-ai/glm-5",
            "x-ai/grok-3-mini"
        ],
        "audit_model": "anthropic/claude-sonnet-4.6",
        "consensus_model": "anthropic/claude-sonnet-4.6",
        "max_reflect_times": 3,
        "reliability_threshold": 70,
        "max_retry": 3
    },
    "n1n": {
        "base_url": "https://api.n1n.ai/v1",
        "api": "your-api-key-here",
        "parm_collect_model": "gpt-4o",
        "report_model": "claude-sonnet-4-6",
        "annotation_model": [
            "gpt-4o",
            "claude-sonnet-4-6",
            "qwen3.5-397b-a17b",
            "deepseek-v3.2"
        ],
        "audit_model": "claude-sonnet-4-6",
        "consensus_model": "claude-sonnet-4-6",
        "max_reflect_times": 5,
        "reliability_threshold": 70,
        "max_retry": 3
    }
}
```

### 配置字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|:----:|:------:|------|
| `base_url` | string | ✅ | - | API 基础地址 |
| `api` | string | ✅ | - | API 密钥 |
| `parm_collect_model` | string | ✅ | - | 参数收集模型，用于交互式参数映射 |
| `annotation_model` | array | ✅ | - | 注释模型列表，支持多模型并行注释 |
| `audit_model` | string | ✅ | - | 审核模型，检测基因幻觉和生物学合理性 |
| `consensus_model` | string | ✅ | - | 共识模型，整合多模型预测结果 |
| `report_model` | string | ✅ | - | 报告生成模型，输出 Markdown 分析报告 |
| `max_reflect_times` | integer | ❌ | 5 | 最大反思次数（评分低于阈值时触发） |
| `reliability_threshold` | integer | ❌ | 70 | 可靠性阈值（0-100） |
| `max_retry` | integer | ❌ | 3 | API 调用最大重试次数 |

### 推荐模型配置

| 用途 | 推荐模型 | 说明 |
|------|----------|------|
| 参数收集 | gpt-4o-mini | 快速、低成本 |
| 注释 | gpt-4o, claude-sonnet, qwen | 多模型提高准确性 |
| 审核 | claude-sonnet-4.6 | 高质量推理能力 |
| 共识 | claude-sonnet-4.6 | 复杂信息整合 |
| 报告 | gpt-4o-mini | 格式化输出 |

## 输入格式

### CSV 文件要求

输入文件应为差异表达分析结果，包含以下列：

| cluster | gene | p_val_adj | avg_log2FC |
|:-------:|:----:|:---------:|:----------:|
| 0 | CD3D | 1.2e-50 | 2.3 |
| 0 | CD3E | 3.4e-45 | 1.9 |
| 0 | CCR7 | 5.6e-60 | 3.1 |
| 1 | CD79A | 2.1e-55 | 2.8 |
| 1 | MS4A1 | 8.9e-48 | 2.5 |

### 列名说明

- **cluster**: 聚类编号（必须）
- **gene**: 基因名称（必须）
- **p_val_adj**: 校正后 P 值（可选，用于排序）
- **avg_log2FC**: 平均 log2 倍数变化（可选，用于排序）

> 程序会交互式地识别列名，支持自定义命名。

## 输出结果

### 目录结构

```
results/
├── report/
│   ├── report_0.md                    # Cluster 0 分析报告
│   ├── report_1.md                    # Cluster 1 分析报告
│   ├── final_annotation_0.csv         # Cluster 0 注释结果
│   └── final_annotation_all_clusters.csv  # 所有 Cluster 汇总
└── log/
    └── 0/
        ├── ann_results.json           # 原始注释结果
        ├── audit_results.json         # 审核评分
        ├── consensus_results.json     # 共识分析
        └── metadata.json              # 运行元数据
```

## 工作流程

```
┌─────────────────┐
│   参数收集      │  基于LLM交互式识别数据列名、物种、组织等信息
└────────┬────────┘
         ▼
┌─────────────────┐
│ 多模型并行注释   │  多个 LLM 同时对每个 Cluster 进行注释
└────────┬────────┘
         ▼
┌─────────────────┐
│   自动审核      │  检测基因幻觉，评估生物学合理性
└────────┬────────┘
         ▼
┌─────────────────┐
│  反思修正？     │  评分 < 阈值？→ 触发反思，最多 N 次
└────────┬────────┘
         ▼
┌─────────────────┐
│   共识整合      │  整合多模型预测，计算一致性
└────────┬────────┘
         ▼
┌─────────────────┐
│   生成报告      │  输出 Markdown + html整合报告 + CSV 结果
└─────────────────┘
```

## 项目结构

```
ohmycelltype/
├── ohmycelltype/
│   ├── __init__.py         # 包入口，JSON 工具函数
│   ├── cli.py              # CLI 命令入口
│   ├── config.py           # 配置管理
│   ├── workflow.py         # 主工作流
│   ├── llm/                # LLM 提供商
│   │   ├── base.py         # 抽象基类
│   │   ├── message.py      # 消息管理
│   │   ├── n1n.py          # N1N 提供商
│   │   └── openrouter.py   # OpenRouter 提供商
│   ├── nodes/              # 工作流节点
│   │   ├── paramcollector_node.py  # 参数收集
│   │   ├── anno_cluster_node.py    # 注释节点
│   │   ├── audit_ann_node.py       # 审核节点
│   │   ├── consensus_node.py       # 共识节点
│   │   └── report_node.py          # 报告节点
│   ├── state/              # 状态管理
│   │   └── state.py        # 数据类定义
│   ├── prompt/             # Prompt 模板
│   │   └── prompt.py       # 所有提示词
│   └── tools/              # 工具函数
│       ├── logger.py       # 日志输出
│       ├── utils.py        # 通用工具
│       └── render.py       # HTML 报告生成
├── setup.py
└── README.md
```

## API 使用

```python
from ohmycelltype.workflow import CelltypeWorkflow

# 创建工作流实例
workflow = CelltypeWorkflow(
    marker_table='marker_genes.csv',
    outdir='./results',
    provider='openrouter'
)

# 参数收集
workflow.collect_parms()

# 执行注释
workflow.multi_cluster_annotation()
```

## 开发路线

### 已完成 ✅

| 功能 | 说明 |
|------|------|
| LLM 抽象层 | 统一的 LLM 接口，支持多提供商 |
| 多模型并行注释 | ThreadPoolExecutor 并行调用 |
| 基因幻觉检测 | 审核 Prompt 检测不存在的基因 |
| 共识引擎 | 计算一致性比例和信息熵 |
| 自我反思机制 | 低评分自动重新注释 |
| 交互式参数收集 | 对话式识别数据结构 |
| Markdown 报告 | 完整推理链分析报告 |
| HTML 可视化 | 交互式报告页面 |
| 多 Cluster 并行 | ThreadPoolExecutor 并行处理 |

### 进行中 🚧

| 功能 | 说明 |
|------|------|
| Prompt 优化 | 提高注释准确性和一致性,减少token消耗 |
| config 配置方法优化 | 优化配置文件配置方法 - html交互式配置 |
| 语言优化 | 优化中文输出 |
| 多进程优化 | ... |
| 单元测试 | pytest 测试套件 |


## 许可证

MIT License
