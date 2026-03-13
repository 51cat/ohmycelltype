# ohmycelltype

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
git clone https://github.com/your-repo/ohmycelltype.git
cd ohmycelltype
pip install -e .
```

## 配置

### 快速初始化

```bash
# 初始化配置文件（创建 ~/.ohmycelltype.json）
ohmycelltype init-config

# 设置 API Key（交互式）
# 会提示输入 provider 名称（默认 n1n）和 API Key
```

### 手动配置

编辑 `~/.ohmycelltype.json`：

```json
{
    "n1n": {
        "base_url": "https://api.n1n.ai/v1",
        "api": "your-api-key-here",
        "parm_collect_model": "gpt-5.4",
        "report_model": "claude-sonnet-4-6",
        "annotation_model": [
            "gpt-5.4",
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

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `base_url` | string | ✅ | API 基础地址，如 `https://api.n1n.ai/v1` |
| `api` | string | ✅ | API 密钥，从服务商获取 |
| `parm_collect_model` | string | ✅ | 参数收集模型，用于交互式参数映射 |
| `annotation_model` | array | ✅ | 注释模型列表，多模型并行注释提高准确性 |
| `audit_model` | string | ✅ | 审核模型，用于检测基因幻觉和生物学合理性 |
| `consensus_model` | string | ✅ | 共识模型，用于整合多模型预测结果 |
| `report_model` | string | ✅ | 报告生成模型，输出 Markdown 分析报告 |
| `max_reflect_times` | integer | ❌ | 最大反思次数，默认 5（评分低于阈值时触发） |
| `reliability_threshold` | integer | ❌ | 可靠性阈值，默认 70（低于此值触发反思） |
| `max_retry` | integer | ❌ | API 调用最大重试次数，默认 3 |

**提示**：
- `annotation_model` 支持多个模型，会并行运行并取共识
- 反思机制：当评分 < `reliability_threshold` 时，自动重新注释（最多 `max_reflect_times` 次）

### 查看配置

```bash
# 显示当前配置（API Key 会脱敏显示）
ohmycelltype show
```

## 使用

```bash
# 注释
ohmycelltype annotate your_marker_genes.csv -o ./results

# 查看版本
ohmycelltype version

# 初始化配置
ohmycelltype init-config

# 查看配置
ohmycelltype show
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
ohmycelltype/
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
