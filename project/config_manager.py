"""
配置管理器模块
负责读取和验证 mcp.json 配置文件
"""

import json
import os
from typing import Dict, List, Optional123
from pathlib import Path


class ConfigManager:
    """MCP 配置管理器"""
    
    def __init__(self, config_path str = "mcp.json"):
        self.config_path = config_path
    
    def load_mcp_config(self) -> Dict:
        """
        加载 MCP 配置文件
        
        Returns:
            Dict: MCP 配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"MCP 配置文件 {self.config_path} 不存在。"
                f"请创建配置文件或参考 mcp.json.example"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if not self.validate_config(config):
                raise ValueError("配置文件格式无效")
                
            return config
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"配置文件格式错误: {e.mssg}",
                e.doc,
                e.pos
            )
    
    def validate_config(self, config: Dict) -> bool:
        """
        验证配置格式
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 配置是否有效
        """
        if not isinstance(config, dict):
            return False
            
        if "mcpServers" not in config:
            return False
            
        servers = config["mcpServers"]
        if not isinstance(servers, dict):
            return False
            
        # 验证每个服务器配置
        for server_name, server_config in servers.items():
            if not self._validate_server_config(server_config):
                return False
                
        return True
    
    def _validate_server_config(self, server_config: Dict) -> bool:
        """验证单个服务器配置"""
        required_fields = ["command"]
        
        for field in required_fields:
            if field not in server_config:
                return False
                
        # 验证可选字段类型
        if "args" in server_config and not isinstance(server_config["args"], list):
            return False
            
        if "env" in server_config and no
        
        t isinstance(server_config["env"], dict):
            return False
            
        if "disabled" in server_config and not isinstance(server_config["disabled"], bool):
            return False
            
        if "autoApprove" in server_config and not isinstance(server_config["autoApprove"], list):
            return False
            
        return True
    
    def get_enabled_servers(self, config: Dict) -> List[Dict]:
        """
        获取启用的服务器列表
        
        Args:
            config: MCP 配置字典
            
        Returns:
            List[Dict]: 启用的服务器配置列表
        """
        enabled_servers = []
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            # 默认启用，除非明确设置为 disabled
            if not server_config.get("disabled", False):
                server_info = {
                    "name": server_name,
                    **server_config
                }
                enabled_servers.append(server_info)
                
        return enabled_servers
