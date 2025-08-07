"""
MCP 客户端管理器模块
负责管理与 MCP 服务器的连接和工具获取
"""

import logging
from typing import List, Dict, Optional, Any
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


logger = logging.getLogger(__name__)


class MCPManager:
    """MCP 客户端管理器"""
    
    def __init__(self):
        self.clients: List[MCPClient] = []
        self.tools: List[Any] = []
        self._active_clients: List[MCPClient] = []
    
    def initialize_clients(self, server_configs: List[Dict]) -> List[MCPClient]:
        """
        初始化 MCP 客户端
        
        Args:
            server_configs: 服务器配置列表
            
        Returns:
            List[MCPClient]: 初始化的客户端列表
        """
        clients = []
        
        for config in server_configs:
            try:
                client = self._create_client(config)
                if client:
                    clients.append(client)
                    logger.info(f"成功连接到 MCP 服务器: {config['name']}")
                    
            except Exception as e:
                logger.error(f"连接 MCP 服务器 {config['name']} 失败: {e}")
                continue
        
        self.clients = clients
        return clients
    
    def _create_client(self, config: Dict) -> Optional[MCPClient]:
        """
        创建单个 MCP 客户端
        
        Args:
            config: 服务器配置
            
        Returns:
            Optional[MCPClient]: MCP 客户端实例
        """
        try:
            # 创建 stdio 服务器参数
            server_params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env", {})
            )
            
            # 创建 MCP 客户端
            client = MCPClient(
                lambda: stdio_client(server_params)
            )
            
            return client
            
        except Exception as e:
            logger.error(f"创建 MCP 客户端失败: {e}")
            return None
    
    def get_all_tools(self) -> List[Any]:
        """
        获取所有可用工具
        
        Returns:
            List[Any]: 工具列表
        """
        all_tools = []
        
        for client in self.clients:
            try:
                # 启动并保持客户端连接
                if client not in self._active_clients:
                    client.__enter__()
                    self._active_clients.append(client)
                
                tools = client.list_tools_sync()
                if tools:
                    all_tools.extend(tools)
                    logger.info(f"从客户端获取到 {len(tools)} 个工具")
                        
            except Exception as e:
                logger.error(f"获取工具失败: {e}")
                continue
        
        self.tools = all_tools
        logger.info(f"总共获取到 {len(all_tools)} 个工具")
        return all_tools
    
    def health_check(self) -> Dict[str, bool]:
        """
        检查所有连接状态
        
        Returns:
            Dict[str, bool]: 连接状态字典
        """
        status = {}
        
        for i, client in enumerate(self.clients):
            try:
                with client:
                    # 尝试列出工具来测试连接
                    client.list_tools_sync()
                    status[f"client_{i}"] = True
                    
            except Exception as e:
                logger.error(f"客户端 {i} 健康检查失败: {e}")
                status[f"client_{i}"] = False
        
        return status
    
    def cleanup(self):
        """清理资源"""
        # 关闭所有活跃的客户端连接
        for client in self._active_clients:
            try:
                client.__exit__(None, None, None)
            except Exception as e:
                logger.error(f"关闭客户端连接失败: {e}")
        
        self._active_clients.clear()
        self.clients.clear()
        self.tools.clear()
        logger.info("MCP 管理器资源已清理")