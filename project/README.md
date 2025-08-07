# 日志分析助手

基于 Strands Agents SDK 的日志分析工具，展示了如何用最少的代码构建实用的 AI 应用。

## 为什么用 Strands Agents SDK

传统方式构建 AI 应用需要处理模型调用、工具集成、对话管理等复杂逻辑。Strands Agents SDK 把这些都简化了：

```python
# 传统方式需要几十行代码处理的逻辑
from strands import Agent
from strands_tools import current_time

agent = Agent(
    system_prompt="你是日志分析助手",
    tools=[current_time]  # 内置工具直接用
)

response = agent("分析今天的错误日志")  # 就这么简单
```

## 功能

- 自然语言查询日志数据
- 自动检测时间异常
- 支持多种数据源（OpenSearch、Elasticsearch 等）
- 命令行交互界面

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制配置文件模板：

```bash
cp mcp.json.example mcp.json
```

编辑 `mcp.json`，配置数据源连接信息。

## 运行

```bash
python3 main.py
```

## 使用

启动后输入查询：

```
> 显示今天的错误日志统计
> 分析最近一周的访问趋势  
> 查找响应时间超过5秒的请求
```

输入 `exit` 退出程序。

## 项目结构

```
project/
├── main.py                 # 程序入口 (50行)
├── log_analyzer_agent.py   # 智能体核心 (80行)
├── time_tools.py          # 自定义工具 (100行)
├── mcp_manager.py         # MCP 连接 (60行)
├── cli_interface.py       # 界面逻辑 (120行)
├── config_manager.py      # 配置处理 (70行)
├── output_formatter.py    # 格式化 (150行)
└── requirements.txt       # 依赖包
```

**总计**: 约 630 行代码实现完整的日志分析工具，其中智能体核心逻辑仅 80 行。

## 配置示例

```json
{
  "mcpServers": {
    "opensearch": {
      "command": "uvx",
      "args": ["opensearch-mcp-server-py"],
      "env": {
        "OPENSEARCH_URL": "https://your-domain.es.amazonaws.com",
        "OPENSEARCH_USERNAME": "username",
        "OPENSEARCH_PASSWORD": "password"
      }
    }
  }
}
```

## SDK 开发体验

### 1. 创建智能体 - 3行代码

```python
from strands import Agent

agent = Agent(system_prompt="你是日志分析助手")
response = agent("查询今天的错误日志")
```

### 2. 添加工具 - 装饰器搞定

```python
from strands import tool

@tool
def validate_timestamps(data: str) -> dict:
    """验证时间戳"""
    return {"valid": True, "count": 100}

# 智能体自动学会使用这个工具
agent = Agent(tools=[validate_timestamps])
```

### 3. 连接数据源 - 配置即可用

```python
# mcp.json 配置好后，工具自动可用
from strands.tools.mcp import MCPClient

client = MCPClient(lambda: stdio_client(params))
tools = client.list_tools_sync()  # 获取所有工具
agent = Agent(tools=tools)        # 智能体立即具备数据查询能力
```

### 4. 内置工具生态

```python
from strands_tools import current_time, calculator, python_repl

# 丰富的预构建工具，开箱即用
agent = Agent(tools=[current_time, calculator, python_repl])
```

## 系统要求

- Python 3.8+
- macOS / Linux / Windows

## 常见问题

**连接失败**: 检查 mcp.json 配置和网络
**查询无结果**: 确认数据源中有对应数据
**时间异常**: 程序会自动检测并提示

## 开发效率对比

**不用 Strands Agents SDK**:
- 需要手动处理模型 API 调用
- 自己实现工具调用逻辑
- 处理对话上下文管理
- 错误处理和重试机制
- 通常需要 200+ 行代码

**使用 Strands Agents SDK**:
- 核心逻辑 50 行代码搞定
- 工具集成只需装饰器
- 内置对话管理
- 自动错误处理
- 专注业务逻辑即可

## 依赖

- strands-agents: 智能体框架
- mcp: 模型上下文协议  
- rich: 终端界面美化