# Strands Agents 开发指南

## 概述

Strands Agents 是一个简单而强大的 Python SDK，用于构建和运行 AI 智能体。它采用模型驱动的方法，只需几行代码就能创建从简单对话助手到复杂自主工作流的各种智能体。

## 核心特性

- **轻量级且灵活**: 简单的智能体循环，开箱即用且完全可定制
- **模型无关**: 支持 Amazon Bedrock、Anthropic、LiteLLM、Llama、Ollama、OpenAI 等多种模型提供商
- **高级功能**: 多智能体系统、自主智能体、流式支持
- **内置 MCP 支持**: 原生支持模型上下文协议 (MCP) 服务器，可访问数千个预构建工具

## 安装和基础设置

### 安装

```bash
# 安装 Strands Agents 核心包
pip install strands-agents

# 安装工具包（可选，包含预构建工具）
pip install strands-agents-tools

# 安装构建器包（可选，用于生成智能体和工具）
pip install strands-agents-builder
```

### 基础配置

默认情况下，Strands Agents 使用 Amazon Bedrock 作为模型提供商，使用 Claude 3.7 Sonnet 模型。

**AWS 凭证配置**:
1. 环境变量: 设置 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, 可选 `AWS_SESSION_TOKEN`
2. AWS 凭证文件: 使用 `aws configure` CLI 命令配置
3. IAM 角色: 在 AWS 服务（如 EC2、ECS、Lambda）上运行时使用 IAM 角色

## 基础智能体创建

### 最简单的智能体

```python
from strands import Agent

# 创建默认设置的智能体
agent = Agent()

# 询问智能体问题
response = agent("告诉我关于智能体 AI 的信息")
print(response)
```

### 带系统提示的智能体

```python
from strands import Agent

# 创建带有系统提示的智能体
agent = Agent(
    system_prompt="""你是一个专业的 Python 编程助手。
    帮助用户解决 Python 编程问题，提供清晰的代码示例和解释。
    始终遵循最佳实践和 PEP 8 编码规范。"""
)

response = agent("如何在 Python 中读取 CSV 文件？")
```

## 工具系统

### 使用预构建工具

```python
from strands import Agent
from strands_tools import calculator, current_time, python_repl

# 创建带有预构建工具的智能体
agent = Agent(tools=[calculator, current_time, python_repl])

# 智能体可以自动选择合适的工具
response = agent("""
我有几个请求：
1. 现在几点了？
2. 计算 3111696 / 74088
3. 用 Python 验证这个计算结果
""")
```

### 创建自定义工具

#### 方法1: 使用 @tool 装饰器

```python
from strands import Agent, tool

@tool
def word_count(text: str) -> int:
    """
    统计文本中的单词数量。
    
    Args:
        text: 要统计的文本
        
    Returns:
        单词数量
    """
    return len(text.split())

@tool
def letter_counter(word: str, letter: str) -> int:
    """
    统计单词中特定字母的出现次数。
    
    Args:
        word: 输入的单词
        letter: 要统计的字母
        
    Returns:
        字母出现的次数
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0
    if len(letter) != 1:
        raise ValueError("letter 参数必须是单个字符")
    return word.lower().count(letter.lower())

# 使用自定义工具创建智能体
agent = Agent(tools=[word_count, letter_counter])
```

#### 方法2: 使用 TOOL_SPEC 字典

```python
from strands.types.tools import ToolResult, ToolUse
from typing import Any

TOOL_SPEC = {
    "name": "my_custom_tool",
    "description": "这个工具的功能描述",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "第一个参数的描述"
                },
                "param2": {
                    "type": "integer", 
                    "description": "第二个参数的描述",
                    "default": 2
                }
            },
            "required": ["param1"]
        }
    }
}

def my_custom_tool(tool: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool["toolUseId"]
    param1 = tool["input"].get("param1")
    param2 = tool["input"].get("param2", 2)
    
    # 工具实现逻辑
    result = f"处理结果: {param1}, {param2}"
    
    return {
        "toolUseId": tool_use_id,
        "status": "success",
        "content": [{"text": result}]
    }

agent = Agent(tools=[my_custom_tool])
```

## 模型提供商配置

### Amazon Bedrock（默认）

```python
from strands import Agent
from strands.models import BedrockModel

# 使用字符串模型 ID
agent = Agent(model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# 或者创建模型提供商实例以获得更多控制
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name="us-west-2",
    temperature=0.3,
    streaming=True  # 启用/禁用流式传输
)
agent = Agent(model=bedrock_model)
```

### 其他模型提供商

```python
# Anthropic
from strands.models.anthropic import AnthropicModel
anthropic_model = AnthropicModel(
    model_id="claude-3-7-sonnet-20250219",
    api_key="your-api-key"
)

# OpenAI
from strands.models.openai import OpenAIModel
openai_model = OpenAIModel(
    model_id="gpt-4",
    api_key="your-api-key"
)

# Ollama（本地运行）
from strands.models.ollama import OllamaModel
ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id="llama3"
)

# LlamaAPI
from strands.models.llamaapi import LlamaAPIModel
llama_model = LlamaAPIModel(
    model_id="Llama-4-Maverick-17B-128E-Instruct-FP8"
)

agent = Agent(model=your_chosen_model)
```

## MCP (模型上下文协议) 集成

### 使用 MCP 工具

```python
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# 连接到 AWS 文档 MCP 服务器
aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

# 使用 MCP 工具
with aws_docs_client:
    tools = aws_docs_client.list_tools_sync()
    agent = Agent(tools=tools)
    response = agent("告诉我关于 Amazon Bedrock 以及如何在 Python 中使用它")
```

## 流式处理和事件捕获

### 异步迭代器

```python
import asyncio
from strands import Agent
from strands_tools import calculator

agent = Agent(
    tools=[calculator],
    callback_handler=None  # 禁用默认回调处理器
)

async def process_streaming_response():
    prompt = "计算 25 * 48 并解释计算过程"
    
    # 获取智能体响应流的异步迭代器
    agent_stream = agent.stream_async(prompt)
    
    # 处理到达的事件
    async for event in agent_stream:
        if "data" in event:
            # 打印生成的文本块
            print(event["data"], end="", flush=True)
        elif "current_tool_use" in event and event["current_tool_use"].get("name"):
            # 打印工具使用信息
            print(f"\n[工具使用: {event['current_tool_use']['name']}]")

# 运行异步事件处理
asyncio.run(process_streaming_response())
```

### 回调处理器

```python
import logging
from strands import Agent
from strands_tools import shell

logger = logging.getLogger("my_agent")

# 定义简单的回调处理器，记录日志而不是打印
tool_use_ids = []
def callback_handler(**kwargs):
    if "data" in kwargs:
        # 记录流式数据块
        logger.info(kwargs["data"], end="")
    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        if tool["toolUseId"] not in tool_use_ids:
            # 记录工具使用
            logger.info(f"\n[使用工具: {tool.get('name')}]")
            tool_use_ids.append(tool["toolUseId"])

# 创建带有回调处理器的智能体
agent = Agent(
    tools=[shell],
    callback_handler=callback_handler
)

result = agent("我使用的是什么操作系统？")
print(result.message)
```

## 多智能体系统

### 1. 智能体作为工具

```python
from strands import Agent, tool

# 创建专门的研究助手
@tool
def research_assistant(query: str) -> str:
    """处理和响应研究相关查询。"""
    research_agent = Agent(
        system_prompt="你是一个专业的研究助手，专门进行深度研究和分析。"
    )
    return str(research_agent(query))

# 创建专门的写作助手
@tool  
def writing_assistant(content: str) -> str:
    """帮助改进和编辑写作内容。"""
    writing_agent = Agent(
        system_prompt="你是一个专业的写作助手，专门帮助改进文本质量和风格。"
    )
    return str(writing_agent(f"请改进以下内容: {content}"))

# 创建协调器智能体
coordinator = Agent(
    system_prompt="你是一个项目协调器，可以委派任务给专门的助手。",
    tools=[research_assistant, writing_assistant]
)

response = coordinator("研究人工智能的最新发展，然后写一份简洁的报告")
```

### 2. 智能体群体

```python
from strands import Agent
from strands_tools import swarm

agent = Agent(tools=[swarm])
result = agent.tool.swarm(
    task="分析这个数据集并识别市场趋势",
    swarm_size=4,
    coordination_pattern="collaborative"
)
```

### 3. 智能体图

```python
from strands import Agent
from strands_tools import agent_graph

agent = Agent(tools=[agent_graph])
agent.tool.agent_graph(
    action="create",
    graph_id="research_team",
    topology={
        "type": "star",
        "nodes": [
            {"id": "coordinator", "role": "team_lead"},
            {"id": "data_analyst", "role": "analyst"}, 
            {"id": "domain_expert", "role": "expert"}
        ],
        "edges": [
            {"from": "coordinator", "to": "data_analyst"},
            {"from": "coordinator", "to": "domain_expert"}
        ]
    }
)
```

## 调试和日志记录

### 启用调试日志

```python
import logging
from strands import Agent

# 启用 Strands 调试日志级别
logging.getLogger("strands").setLevel(logging.DEBUG)

# 设置日志格式并将日志流式传输到 stderr
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

agent = Agent()
agent("你好！")
```

## 实际应用示例

### 1. 配方助手机器人

```python
from strands import Agent, tool
from duckduckgo_search import DDGS

@tool
def websearch(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
    """搜索网络获取最新信息。"""
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "未找到结果。"
    except Exception as e:
        return f"搜索错误: {e}"

# 创建配方助手智能体
recipe_agent = Agent(
    system_prompt="""你是 RecipeBot，一个有用的烹饪助手。
    根据食材帮助用户找到食谱并回答烹饪问题。
    当用户提到食材或需要查找烹饪信息时，使用 websearch 工具查找食谱。""",
    tools=[websearch]
)

# 交互式对话循环
print("\n👨‍🍳 RecipeBot: 问我关于食谱或烹饪的问题！输入 'exit' 退出。\n")

while True:
    user_input = input("\n你 > ")
    if user_input.lower() == "exit":
        print("祝你烹饪愉快！🍽️")
        break
    response = recipe_agent(user_input)
    print(f"\nRecipeBot > {response}")
```

### 2. JIRA 票据助手

```python
from strands import Agent
from strands_tools import file_read

# 自定义 JIRA 工具（简化示例）
@tool
def create_jira_ticket(title: str, description: str, priority: str = "Medium") -> str:
    """创建 JIRA 票据。"""
    # 这里应该是实际的 JIRA API 调用
    return f"已创建 JIRA 票据: {title} (优先级: {priority})"

ticket_agent = Agent(
    system_prompt="""你是一个敏捷开发专家，专门将会议记录分解为可操作的任务。
    根据双周规划会议的高级计划项目创建结构良好、详细的 Jira 票据。""",
    tools=[file_read, create_jira_ticket]
)

# 使用示例
query = input("\n添加你的双周冲刺会议记录或写一个 .txt 文件名 > ")
ticket_agent(f"使用会议记录创建 5 个 Jira 票据: {query}")
```

## 最佳实践

### 1. 工具设计原则

- **清晰命名**: 使用描述性的工具名称
- **详细文档**: 为工具功能和参数提供详细描述
- **错误处理**: 在工具中包含适当的错误处理
- **参数验证**: 在处理前验证输入
- **结构化返回**: 返回智能体易于理解的结构化数据

### 2. 智能体配置

- **明确的系统提示**: 提供清晰、具体的角色和行为指导
- **适当的工具选择**: 只包含智能体需要的工具
- **模型选择**: 根据任务复杂度选择合适的模型
- **温度设置**: 根据需要的创造性程度调整温度参数

### 3. 安全考虑

- **输入验证**: 始终验证用户输入
- **权限控制**: 限制工具的访问权限
- **敏感数据**: 避免在日志中记录敏感信息
- **错误处理**: 优雅地处理错误，不暴露系统信息

### 4. 性能优化

- **流式处理**: 对于长时间运行的任务使用流式处理
- **状态管理**: 合理管理智能体状态和会话
- **资源清理**: 及时清理不需要的资源
- **缓存策略**: 对重复查询实施缓存

## 环境变量配置

常用的环境变量配置：

```bash
# AWS 配置
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2

# 开发模式（跳过工具确认）
BYPASS_TOOL_CONSENT=true

# Python REPL 配置
PYTHON_REPL_INTERACTIVE=true
PYTHON_REPL_RESET_STATE=false

# 计算器配置
CALCULATOR_PRECISION=10
CALCULATOR_SCIENTIFIC=false
```

## 故障排除

### 常见问题

1. **模型访问错误**: 确保在 Amazon Bedrock 控制台中启用了模型访问
2. **凭证问题**: 检查 AWS 凭证配置是否正确
3. **工具执行失败**: 验证工具参数和权限
4. **内存问题**: 对于长时间运行的智能体，考虑状态重置

### 调试技巧

1. 启用详细日志记录
2. 使用回调处理器监控执行过程
3. 检查工具输入和输出
4. 验证模型配置

这个指南涵盖了 Strands Agents 的核心概念和实际应用。根据具体需求，你可以组合这些功能来构建强大的 AI 智能体系统。