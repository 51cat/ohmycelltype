# CelltypeAgent

一个基于多模型协作的细胞类型自动注释系统，用于单细胞RNA测序数据的自动细胞类型注释。

## 项目目的

1. 开发一个基于多模型细胞类型注释的多agent协作系统
2. 不依赖任何框架（如LangChain），从零实现，主要目的是学习

## 功能特性

- **多LLM模型支持**：GPT、Claude、MiniMax、Qwen等多种模型并行注释
- **自动参数收集**：通过对话式交互自动识别数据结构并配置参数
- **多模型共识机制**：整合多个模型的注释结果，提高准确性
- **注释审核与反思**：自动评估注释可靠性，支持多轮反思修正
- **详细的推理过程**：记录完整的细胞类型判定依据
- **多物种/组织支持**：支持Human、Mouse等多种物种和组织类型

## 安装

```bash
# 克隆仓库
git clone https://github.com/your-repo/CelltypeAgent.git
cd CelltypeAgent

# 安装依赖
pip install -e .
```

## 项目结构

```
celltypeAgent/
├── celltypeAgent/
│   ├── __init__.py              # 包初始化，JSON工具函数
│   ├── agent2.py                # 主agent类，工作流编排
│   ├── config.json              # API配置
│   ├── llm/                     # LLM接口层
│   │   ├── base.py              # LLM抽象基类
│   │   ├── n1n.py               # N1N API实现
│   │   ├── openrouter.py        # OpenRouter实现
│   │   ├── message.py           # 消息历史管理
│   │   └── tool.py              # 工具文档提取
│   ├── nodes/                   # 工作流节点
│   │   ├── paramcollector_node.py   # 参数收集节点
│   │   ├── anno_cluster_node.py     # 细胞类型注释节点
│   │   ├── audit_ann_node.py        # 注释审核节点
│   │   └── consensus_node.py        # 多模型共识节点
│   ├── state/                   # 状态管理
│   │   └── state.py             # 数据类定义
│   ├── prompt/                  # 提示模板
│   │   └── prompt.py            # 所有提示词
│   └── tools/                   # 工具函数
│       ├── utils.py             # 通用工具
│       └── agent_tools.py       # Agent专用工具
├── example_data/                # 示例数据
├── work/                        # 输出目录
└── setup.py                     # 包配置
```

## 工作流程

```
┌─────────────────┐
│  参数收集节点    │  交互式收集物种、组织、列映射等参数
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  细胞类型注释    │  多个LLM模型并行注释
│  (多个模型)      │  输出: cell_type, cell_subtype, reasoning
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  注释审核节点    │  评估注释可靠性 (0-100分)
│                 │  检测: Gene Hallucination, 生物学合理性
└────────┬────────┘
         │
         ▼ (若评分 < 80)
┌─────────────────┐
│  反思修正        │  最多5轮反思，优化注释结果
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  共识节点        │  整合多模型结果，输出最终注释
└─────────────────┘
```

## 开发状态

### 已完成

- ✅ LLM基础接口层（BaseLLM抽象类）
- ✅ N1N API集成
- ✅ 消息历史管理（Message类）
- ✅ 参数收集节点（交互式参数配置）
- ✅ 细胞类型注释节点
- ✅ 注释审核节点（可靠性评分、Gene Hallucination检测）
- ✅ 共识节点（多模型结果整合）
- ✅ 反思修正机制（最多5轮）
- ✅ 状态管理（dataclass定义）
- ✅ 提示模板设计

### 开发中

- ⌛️ 并行处理多个簇
- ⌛️ 完整的错误处理和重试机制
- ⌛️ 日志系统完善
- ⌛️ 单元测试

### 计划中

- ⌛️ 支持更多LLM提供商
- ⌛️ Web界面
- ⌛️ 结果可视化
- ⌛️ 批量处理优化

## 依赖

- `openai` - OpenAI API客户端
- `pandas` - 数据处理
- `requests` - HTTP请求

可选：
- `openpyxl` - Excel文件处理
