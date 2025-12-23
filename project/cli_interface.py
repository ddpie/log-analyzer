"""
命令行界面模块
负责处理用户交互和命令行界面
"""

import logging
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from strands import Agent
from output_formatter import OutputFormatter


logger = logging.getLogger(__name__)


class CLIInterface:
    """命令行界面管理器"""
    
    def __init__(self):
        self.console = Console()
        self.running = False
        self.formatter = OutputFormatter()  # 统一使用格式化器
    
    def display_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = Text()
        welcome_text.append("🔍 日志分析手", style="bold blue")
        welcome_text.append("\n\n基于 Strands Agents 的智能日志分析工具")
        welcome_text.append("\n\n功能特性:")
        welcome_text.append("\n• 自然语言查询日志数据", style="green")
        welcome_text.append("\n• 智能分析业务指标和趋势", style="green")
        welcome_text.append("\n• 通过 MCP 协议连接多种数据源", style="green")
        welcome_text.append("\n\n使用说明:")
        welcome_text.append("\n• 直接输入您的查询问题")
        welcome_text.append("\n• 输入 'exit' 或 'quit' 退出程序")
        welcome_text.append("\n• 输入 'help' 查看更多帮助信息")
        
        panel = Panel(
            welcome_text,
            title="欢迎使用",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def start_interactive_mode(self, agent: Agent):
        """
        启动交互模式
        
        Args:
            agent: 日志分析智能体
        """
        self.display_welcome_message()
        self.running = True
        
        try:
            while self.running:
                # 获取用户输入
                
                user_input = self.console.input("[bold cyan]请输入您的查询[/bold cyan] > ")
                
                # 处理用户输入
                if not self.handle_user_input(user_input, agent):
                    break
                    
        except KeyboardInterrupt:
        except Exception as e:
            self.console.print(f"\n[red]程序运行出错: {e}[/red]")
        finally:
            self.display_goodbye_message()
    
    def handle_user_input(self, input_text: str, agent: Agent) -> bool:
        """
        处理用户输入
        
        Args:
            input_text: 用户输入文本
            agent: 日志分析智能体
            
        Returns:
            bool: 是否继续运行程序
        """
        # 清理输入
        input_text = input_text.strip()
        
        # 检查退出命令
        if input_text.lower() in ['exit', 'quit', '退出']:
            return False
        
        # 检查帮助命令
        if input_text.lower() in ['help', '帮助']:
            self.display_help()
            return True
        
        # 检查空输入
        if not input_text:
            self.console.print("[yellow]请输入您的查询问题[/yellow]")
            return True
        
        # 处理查询
        try:
            self.console.print("\n[dim]正在分析您的查询...[/dim]")
            
            # 调用智能体分析
            from log_analyzer_agent import LogAnalyzerAgent
            if isinstance(agent, LogAnalyzerAgent):
                result = agent.analyze_query(input_text)
            else:
                # 直接调用 agent
                response = agent(input_text)
                result = str(response.message) if hasattr(response, 'message') else str(response)
            
            # 显示结果
            self.display_result(result)
            
        except Exception as e:
            # 使用格式化器处理错误信息
            error_msg = self.formatter.format_error_message(e)
            self.console.print(f"[red]{error_msg}[/red]")
            logger.error(f"查询处理错误: {e}")
        
        return True
    
    def display_result(self, result: str):
        """
        显示分析结果
        
        Args:
            result: 分析结果文本
        """
        # 使用统一的格式化器清理结果
        cleaned_result = self.formatter.format_result(result)
        
        # 创建结果面板
        result_panel = Panel(
            cleaned_result,
            title="📊 分析结果",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(result_panel)
        self.console.print()
    
    def display_help(self):
        """显示帮助信息"""
        help_text = Text()
        help_text.append("\n\n可用命令:")
        help_text.append("\n• help/帮助 - 显示此帮助信息", style="cyan")
        help_text.append("\n• exit/quit/退出 - 退出程序", style="cyan")
        help_text.append("\n\n查询示例:")
        help_text.append("\n• '显示今天的错误日志统计'", style="green")
        help_text.append("\n• '分析最近一周的用户访问趋势'", style="green")
        help_text.append("\n• '查找响应时间异常的请求'", style="green")
        help_text.append("\n• '统计各个接口的调用次数'", style="green")
        
        help_panel = Panel(
            help_text,
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(help_panel)
        self.console.print()
    
    def display_goodbye_message(self):
        """显示退出信息"""
        goodbye_text = Text("👋 感谢使用日志分析助手，再见！", style="bold blue")
        self.console.print()
        self.console.print(goodbye_text)
    
    def display_error(self, error_message: str):
        """
        显示错误信息
        
        Args:
            error_message: 错误信息
        """
        error_panel = Panel(
            f"❌ {error_message}",
            title="错误",
            border_style="red1",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(error_panel)
        self.console.print()
    
    def display_status(self, status_message: str):
        """
        显示状态信息
        
        Args:
            status_message: 状态信息
        """
        self.console.print(f"[dim]{status_message}[/dim]")
