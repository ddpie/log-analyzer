"""
输出格式化工具模块
负责清理和格式化智能体的输出结果
"""

import re
import logging
from typing import List, Optional, Dict


logger = logging.getLogger(__name__)


class OutputFormatter:
    """输出格式化器"""
    
    def __init__(self):
        # 定义需要清理的模式
        self.cleanup_patterns = [
            # 移除 Rich 格式标记
            (r'\[/?[a-zA-Z0-9_\s#:;,.-]+\]', ''),
            # 移除 Markdown 粗体标记
            (r'\*\*([^*]+)\*\*', r'\1'),
            # 移除 Markdown 斜体标记
            (r'\*([^*]+)\*', r'\1'),
            # 移除 Markdown 标题标记
            (r'^#+\s*', ''),
            # 移除代码块标记
            (r'```[a-zA-Z]*\n?', ''),
            (r'```', ''),
            # 移除行内代码标记
            (r'`([^`]+)`', r'\1'),
            # 处理转义字符
            (r'\\n', '\n'),
            (r'\\t', '    '),
            (r'\\r', '\r'),
            (r'\\"', '"'),
            (r"\\'", "'"),
        ]
        
        # 定义段落分隔符
        self.section_indicators = [
            '分析摘要', '详细数据', '关键发现', '统计结果', 
            '趋势分析', '异常检测', '建议', '总结', '结论'
        ]
    
    def format_result(self, text: str) -> str:
        """
        格式化分析结果文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 格式化后的文本
        """
        if not text or not text.strip():
            return "未获取到分析结果"
        
        try:
            # 基础清理
            cleaned = self._basic_cleanup(text)
            
            # 处理结构化内容
            cleaned = self._process_structured_content(cleaned)
            
            # 处理行结构
            cleaned = self._process_lines(cleaned)
            
            # 最终清理
            cleaned = self._final_cleanup(cleaned)
            
            return cleaned if cleaned.strip() else "分析完成，但未生成具体结果"
            
        except Exception as e:
            logger.error(f"格式化输出时出错: {e}")
            return f"格式化输出时出错，原始结果：\n{text}"
    
    def _basic_cleanup(self, text: str) -> str:
        """基础文本清理"""
        cleaned = text
        
        # 先处理双反斜杠
        cleaned = cleaned.replace('\\\\', '\\')
        
        # 应用清理模式
        for pattern, replacement in self.cleanup_patterns:
            try:
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)
            except re.error as e:
                logger.warning(f"正则表达式错误: {pattern} -> {e}")
                continue
        
        return cleaned
    
    def _process_structured_content(self, text: str) -> str:
        """处理结构化内容，如表格、列表等"""
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                processed_lines.append('')
                continue
            
            # 检测并格式化表格行
            if '|' in line and line.count('|') >= 2:
                # 简化表格格式
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if parts:
                    processed_lines.append('  ' + ' | '.join(parts))
                continue
            
            # 检测段落标题
            if any(indicator in line for indicator in self.section_indicators):
                if processed_lines and processed_lines[-1]:
                    processed_lines.append('')  # 段落前加空行
                # 确保标题格式正确
                if not line.endswith(':'):
                    line = line.rstrip('：') + ':'
                processed_lines.append(line)
                continue
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _process_lines(self, text: str) -> str:
        """处理行结构和格式"""
        lines = text.split('\n')
        processed_lines = []
        prev_line_empty = False
        in_list = False
        
        for i, line in enumerate(lines):
            # 移除行首行尾空白
            line = line.strip()
            
            if not line:
                # 处理空行 - 避免连续多个空行
                if not prev_line_empty and processed_lines:
                    processed_lines.append('')
                prev_line_empty = True
                in_list = False
            else:
                # 处理非空行
                formatted_line = self._format_line(line)
                
                # 检测列表项
                is_list_item = formatted_line.startswith('• ') or re.match(r'^\d+\.\s', formatted_line)
                
                # 在列表开始前添加空行
                if is_list_item and not in_list and processed_lines and processed_lines[-1]:
                    processed_lines.append('')
                
                processed_lines.append(formatted_line)
                prev_line_empty = False
                in_list = is_list_item
        
        return '\n'.join(processed_lines)
    
    def _format_line(self, line: str) -> str:
        """格式化单行文本"""
        # 统一列表标记
        line = re.sub(r'^[•\-\*\+]\s*', '• ', line)
        
        # 处理数字列表
        line = re.sub(r'^(\d+)[\.\)]\s*', r'\1. ', line)
        
        # 移除行首的多余符号
        line = re.sub(r'^[>\|]+\s*', '', line)
        
        # 处理冒号后的内容格式
        if ':' in line and not line.endswith(':'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                key, value = parts
                value = value.strip()
                if value:
                    line = f"{key.strip()}: {value}"
        
        return line
    
    def _final_cleanup(self, text: str) -> str:
        """最终清理"""
        # 移除多余的连续空行
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        # 移除开头和结尾的空白
        text = text.strip()
        
        # 确保段落之间有适当的间距
        text = self._ensure_paragraph_spacing(text)
        
        # 修复常见的格式问题
        text = self._fix_common_issues(text)
        
        return text
    
    def _ensure_paragraph_spacing(self, text: str) -> str:
        """确保段落间距合适"""
        lines = text.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            # 在特定情况下添加空行
            if (i < len(lines) - 1 and 
                line and 
                lines[i + 1] and 
                not line.startswith('•') and 
                not lines[i + 1].startswith('•') and
                (line.endswith(':') or 
                 any(indicator in line for indicator in self.section_indicators))):
                result_lines.append('')
        
        return '\n'.join(result_lines)
    
    def _fix_common_issues(self, text: str) -> str:
        """修复常见的格式问题"""
        # 修复数字和单位之间的空格
        text = re.sub(r'(\d+)\s*%', r'\1%', text)
        text = re.sub(r'(\d+)\s*(MB|GB|KB|ms|s)', r'\1\2', text)
        
        # 修复时间格式
        text = re.sub(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})', 
                     r'\1-\2-\3 \4:\5:\6', text)
        
        # 确保冒号后有空格
        text = re.sub(r':([^\s])', r': \1', text)
        
        return text
    
    def format_error_message(self, error: Exception) -> str:
        """
        格式化错误信息
        
        Args:
            error: 异常对象
            
        Returns:
            str: 格式化的错误信息
        """
        error_msg = str(error).strip()
        
        # 错误类型映射
        error_mappings = {
            'connection': "连接错误：无法连接到数据源，请检查网络连接和配置",
            'timeout': "请求超时：数据查询时间过长，请尝试缩小查询范围",
            'permission': "权限错误：没有访问数据源的权限，请检查认证配置",
            'auth': "认证错误：身份验证失败，请检查凭据配置",
            'not found': "数据未找到：请检查查询条件和数据源配置",
            'invalid': "参数错误：查询参数无效，请检查输入格式",
            'rate limit': "请求频率限制：请求过于频繁，请稍后重试"
        }
        
        # 检查错误类型
        error_lower = error_msg.lower()
        for keyword, message in error_mappings.items():
            if keyword in error_lower:
                return message
        
        # 清理错误信息
        cleaned_error = self._basic_cleanup(error_msg)
        return f"处理查询时出现错误：{cleaned_error}"
    
    def format_status_message(self, message: str, status_type: str = "info") -> str:
        """
        格式化状态信息
        
        Args:
            message: 状态信息
            status_type: 状态类型 (info, warning, error, success)
            
        Returns:
            str: 格式化的状态信息
        """
        icons = {
            "info": "ℹ️",
            "warning": "⚠️", 
            "error": "❌",
            "success": "✅",
            "loading": "⏳",
            "processing": "🔄"
        }
        
        icon = icons.get(status_type, "ℹ️")
        return f"{icon} {message}"
    
    def format_summary(self, data: Dict) -> str:
        """
        格式化数据摘要
        
        Args:
            data: 数据字典
            
        Returns:
            str: 格式化的摘要
        """
        if not data:
            return "无数据可显示"
        
        lines = []
        
        for key, value in data.items():
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            
            # 格式化键名
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"• {formatted_key}: {formatted_value}")
        
        return '\n'.join(lines)