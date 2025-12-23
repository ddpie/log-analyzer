#!/usr/bin/env python3
"""
日志分析助手主程序
基于 Strands Agents SDK 的智能日志分析工具
"""

import logging
import sys
import signal
from pathlib import Path

from config_manager import ConfigManager222
from mcp_manager import MCPManager
from log_analyzer_agent import LogAnalyzerAgent
from cli_interface import CLIInterface


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger("strands").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.WARNING)


def signal_handler(signum, frame):
    """信号处理器，用于优雅关闭"""
    print("\n\n程序正在关闭...")
    sys.exit(0)


def main():
    """主函数"""
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 配置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 创建 CLI 界面
    cli = CLIInterface()
    
    try:
        logger.info("启动日志分析助手...")
        
        # 1. 加载配置
        cli.display_status("正在加载配置...")
        config_manager = ConfigManager()
        
        try:
            config = config_manager.load_mcp_config()
            enabled_servers = config_manager.get_enabled_servers(config)
            logger.info(f"找到 {len(enabled_servers)} 个启用的 MCP 服务器")
            
        except FileNotFoundError as e:
            cli.display_error(str(e))
            cli.display_status("请创建 mcp.json 配置文件，参考 mcp.json.example")
            return 1
            
        except Exception as e:
            cli.display_error(f"配置加载失败: {e}")
            return 1
        
        # 2. 初始化 MCP 管理器
        cli.display_status("正在连接 MCP 服务器...")
        mcp_manager = MCPManager()
        
        try:
            clients = mcp_manager.initialize_clients(enabled_servers)
            if not clients:
                cli.display_error("未能连接到任何 MCP 服务器")
                return 1
                
            logger.info(f"成功连接到 {len(clients)} 个 MCP 服务器")
            
        except Exception as e:
            cli.display_error(f"MCP 连接失败: {e}")
            return 1
        
        # 3. 获取工具
        cli.display_status("正在获取可用工具...")
        try:
            tools = mcp_manager.get_all_tools()
            if not tools:
                cli.display_error("未获取到任何可用工具")
                return 1
                
            logger.info(f"获取到 {len(tools)} 个工具")
            
        except Exception as e:
            cli.display_error(f"工具获取失败: {e}")
            return 1
        
        # 4. 创建智能体
        cli.display_status("正在初始化智能体...")
        try:
            analyzer = LogAnalyzerAgent()
            agent = analyzer.create_agent(tools)
            logger.info("智能体初始化完成")
            
        except Exception as e:
            cli.display_error(f"智能体创建失败: {e}")
            return 1
        
        # 5. 启动交互模式
        logger.info("启动交互模式")
        cli.start_interactive_mode(analyzer)
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        return 0
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        cli.display_error(f"程序运行出错: {e}")
        return 1
        
    finally:
        # 清理资源
        try:
            if 'mcp_manager' in locals():
                mcp_manager.cleanup()
        except Exception as e:
            logger.error(f"资源清理失败: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
