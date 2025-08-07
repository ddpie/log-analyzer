"""
日志分析智能体核心模块
负责创建和管理专门用于日志分析的 Strands Agent
"""

import logging
from typing import List, Any, Optional, Dict
from strands import Agent
from strands_tools import current_time
from time_tools import validate_log_timestamps, format_time_analysis, get_time_filter_suggestion


logger = logging.getLogger(__name__)


class LogAnalyzerAgent:
    """日志分析智能体"""
    
    def __init__(self):
        self.agent: Optional[Agent] = None
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """创建专门的系统提示"""
        return """你是一个专业的日志分析助手，专门分析业务日志数据。

核心能力：
1. 理解用户的自然语言查询意图
2. 使用 MCP 工具查询日志数据源
3. 分析日志数据并识别模式、趋势和异常
4. 使用时间工具进行时间数据验证和分析：
   - current_time: 获取当前准确时间
   - validate_log_timestamps: 验证日志时间戳合理性
   - format_time_analysis: 格式化时间分析报告
   - get_time_filter_suggestion: 生成合理的时间查询范围
5. 生成清晰易懂的结构化分析报告

分析重点：
- 业务指标和 KPI 统计
- 用户行为模式分析
- 系统性能趋势监控
- 异常和错误模式识别
- 时间序列数据分析
- 时间数据准确性验证

输出格式要求：
请严格按照以下格式输出分析结果：

1. 使用纯文本格式，避免任何 Markdown 标记
2. 使用清晰的段落结构组织内容
3. 用简单的项目符号（•）标记列表项
4. 数据统计使用 "指标名称: 数值" 格式
5. 时间范围明确标注
6. 段落之间用空行分隔

标准输出模板：
分析摘要:
• 核心发现1
• 核心发现2
• 核心发现3

详细统计:
• 总记录数: X条
• 时间范围: YYYY-MM-DD 到 YYYY-MM-DD
• 关键指标: 具体数值

趋势分析:
• 趋势描述1
• 趋势描述2

异常检测:
• 异常情况1
• 异常情况2

建议措施:
• 建议1
• 建议2

时间数据处理规则：
- 发现日志中有时间数据时，自动使用 validate_log_timestamps 工具验证时间合理性
- 使用 current_time 工具获取当前准确时间作为基准
- 对于未来时间的日志数据，明确标注为异常并分析可能原因
- 使用 get_time_filter_suggestion 工具为用户提供合理的查询时间范围建议
- 使用 format_time_analysis 工具生成专业的时间分析报告

注意事项：
- 所有数字要准确，包含单位
- 时间格式统一使用 YYYY-MM-DD HH:MM:SS
- 百分比保留两位小数
- 避免使用技术术语，用业务语言描述
- 如果数据不足，明确说明限制条件

请始终以专业、准确且格式清晰的方式回答用户的日志分析查询。"""
    
    def create_agent(self, tools: List[Any]) -> Agent:
        """
        创建配置好的智能体
        
        Args:
            tools: 可用工具列表
            
        Returns:
            Agent: 配置好的 Strands Agent
        """
        try:
            # 添加内置时间工具和自定义时间工具到工具列表
            time_tools = [
                current_time, 
                validate_log_timestamps, 
                format_time_analysis, 
                get_time_filter_suggestion
            ]
            enhanced_tools = tools + time_tools
            
            self.agent = Agent(
                system_prompt=self.system_prompt,
                tools=enhanced_tools
            )
            
            logger.info(f"日志分析智能体已创建，包含 {len(enhanced_tools)} 个工具（含 {len(time_tools)} 个时间工具）")
            return self.agent
            
        except Exception as e:
            logger.error(f"创建智能体失败: {e}")
            raise
    
    def analyze_query(self, query: str) -> str:
        """
        处理用户查询并返回分析结果
        
        Args:
            query: 用户查询字符串
            
        Returns:
            str: 分析结果
        """
        if not self.agent:
            raise RuntimeError("智能体未初始化，请先调用 create_agent()")
        
        try:
            logger.info(f"处理用户查询: {query[:100]}...")
            
            # 预处理查询
            processed_query = self._preprocess_query(query)
            
            # 使用智能体处理查询
            response = self.agent(processed_query)
            
            # 提取和处理响应文本
            result = self._extract_response_text(response)
            
            # 后处理结果
            result = self._postprocess_result(result)
            
            logger.info("查询处理完成")
            return result
            
        except Exception as e:
            logger.error(f"查询处理失败: {e}")
            return self._format_error_response(str(e))
    
    def _preprocess_query(self, query: str) -> str:
        """
        预处理用户查询
        
        Args:
            query: 原始查询
            
        Returns:
            str: 处理后的查询
        """
        # 清理查询文本
        query = query.strip()
        
        # 添加上下文提示
        if not any(keyword in query.lower() for keyword in ['分析', '统计', '查询', '显示']):
            query = f"请分析：{query}"
        
        return query
    
    def _extract_response_text(self, response) -> str:
        """
        从响应中提取文本内容
        
        Args:
            response: 智能体响应
            
        Returns:
            str: 提取的文本
        """
        if hasattr(response, 'message'):
            return str(response.message)
        elif hasattr(response, 'content'):
            return str(response.content)
        elif hasattr(response, 'text'):
            return str(response.text)
        else:
            return str(response)
    
    def _postprocess_result(self, result: str) -> str:
        """
        后处理分析结果
        
        Args:
            result: 原始结果
            
        Returns:
            str: 处理后的结果
        """
        if not result or not result.strip():
            return "分析完成，但未生成具体结果。请尝试更具体的查询条件。"
        
        # 基本清理
        result = result.strip()
        
        # 确保结果有意义
        if len(result) < 10:
            return "分析结果过于简短，请尝试更详细的查询。"
        
        return result
    
    def _format_error_response(self, error_msg: str) -> str:
        """
        格式化错误响应
        
        Args:
            error_msg: 错误信息
            
        Returns:
            str: 格式化的错误响应
        """
        # 常见错误的友好提示
        if "timeout" in error_msg.lower():
            return """查询超时，可能的原因：
• 查询范围过大，请缩小时间范围
• 数据源响应缓慢，请稍后重试
• 网络连接不稳定

建议：尝试查询最近几小时或特定时间段的数据。"""
        
        elif "connection" in error_msg.lower():
            return """数据源连接失败：
• 请检查网络连接状态
• 确认数据源配置正确
• 验证访问权限设置

如问题持续，请联系系统管理员。"""
        
        elif "permission" in error_msg.lower() or "auth" in error_msg.lower():
            return """权限验证失败：
• 请检查访问凭据配置
• 确认账户权限设置
• 验证数据源访问策略

请联系管理员检查权限配置。"""
        
        else:
            return f"""处理查询时遇到问题：
• 错误详情：{error_msg}
• 建议：请尝试重新表述查询或联系技术支持

您可以尝试：
• 使用更简单的查询条件
• 缩小数据范围
• 检查查询语法"""
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Returns:
            Dict[str, Any]: 智能体信息
        """
        if not self.agent:
            return {"status": "未初始化"}
        
        return {
            "status": "已初始化",
            "tools_count": len(self.agent.tools) if hasattr(self.agent, 'tools') else 0,
            "system_prompt_length": len(self.system_prompt)
        }