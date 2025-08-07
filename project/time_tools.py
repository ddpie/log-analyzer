"""
时间相关的自定义工具
用于日志分析中的时间验证和处理
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from strands import tool


logger = logging.getLogger(__name__)


@tool
def validate_log_timestamps(log_timestamps: str) -> Dict[str, Any]:
    """
    验证日志时间戳的合理性，检测时间异常
    
    Args:
        log_timestamps: 日志时间戳列表，用逗号分隔，格式如 "2025-02-13 02:42:16,2025-07-15 23:26:11"
        
    Returns:
        Dict[str, Any]: 时间验证结果
    """
    try:
        current_time = datetime.now(timezone.utc)
        timestamps = [ts.strip() for ts in log_timestamps.split(',')]
        
        results = {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_timestamps": len(timestamps),
            "future_timestamps": [],
            "past_timestamps": [],
            "invalid_timestamps": [],
            "time_range": {},
            "anomalies": []
        }
        
        valid_datetimes = []
        
        for ts in timestamps:
            try:
                # 尝试解析时间戳
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                valid_datetimes.append(dt)
                
                # 检查是否为未来时间
                if dt > current_time:
                    results["future_timestamps"].append({
                        "timestamp": ts,
                        "days_in_future": (dt - current_time).days
                    })
                else:
                    results["past_timestamps"].append(ts)
                    
            except ValueError:
                results["invalid_timestamps"].append(ts)
        
        # 计算时间范围
        if valid_datetimes:
            min_time = min(valid_datetimes)
            max_time = max(valid_datetimes)
            results["time_range"] = {
                "earliest": min_time.strftime("%Y-%m-%d %H:%M:%S"),
                "latest": max_time.strftime("%Y-%m-%d %H:%M:%S"),
                "span_days": (max_time - min_time).days
            }
        
        # 生成异常报告
        if results["future_timestamps"]:
            results["anomalies"].append({
                "type": "future_timestamps",
                "count": len(results["future_timestamps"]),
                "description": "发现未来时间戳，可能是系统时间配置错误或测试数据"
            })
        
        if results["invalid_timestamps"]:
            results["anomalies"].append({
                "type": "invalid_format",
                "count": len(results["invalid_timestamps"]),
                "description": "时间戳格式无效，无法解析"
            })
        
        # 检查时间跨度异常
        if valid_datetimes and results["time_range"]["span_days"] > 365:
            results["anomalies"].append({
                "type": "large_time_span",
                "span_days": results["time_range"]["span_days"],
                "description": "时间跨度超过一年，请确认数据范围是否正确"
            })
        
        return results
        
    except Exception as e:
        logger.error(f"时间戳验证失败: {e}")
        return {
            "error": str(e),
            "current_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }


@tool
def format_time_analysis(analysis_data: str) -> str:
    """
    格式化时间分析结果为易读的报告
    
    Args:
        analysis_data: JSON格式的分析数据
        
    Returns:
        str: 格式化的分析报告
    """
    try:
        import json
        data = json.loads(analysis_data)
        
        report = []
        report.append("时间数据验证报告")
        report.append("=" * 30)
        
        # 基本信息
        report.append(f"当前时间: {data.get('current_time', 'N/A')}")
        report.append(f"总时间戳数: {data.get('total_timestamps', 0)}")
        
        # 时间范围
        if 'time_range' in data and data['time_range']:
            tr = data['time_range']
            report.append(f"时间范围: {tr.get('earliest', 'N/A')} 到 {tr.get('latest', 'N/A')}")
            report.append(f"跨度: {tr.get('span_days', 0)} 天")
        
        # 异常情况
        if data.get('anomalies'):
            report.append("\n异常检测:")
            for anomaly in data['anomalies']:
                report.append(f"• {anomaly.get('description', 'N/A')}")
                if 'count' in anomaly:
                    report.append(f"  影响数量: {anomaly['count']}")
        
        # 未来时间戳详情
        if data.get('future_timestamps'):
            report.append("\n未来时间戳详情:")
            for ft in data['future_timestamps'][:5]:  # 只显示前5个
                report.append(f"• {ft['timestamp']} (未来 {ft['days_in_future']} 天)")
        
        # 建议
        report.append("\n建议措施:")
        if data.get('future_timestamps'):
            report.append("• 检查系统时间配置")
            report.append("• 确认是否为测试数据")
            report.append("• 验证数据源时间同步")
        
        if data.get('invalid_timestamps'):
            report.append("• 检查时间戳格式标准化")
            report.append("• 验证数据采集过程")
        
        return "\n".join(report)
        
    except Exception as e:
        return f"格式化报告失败: {e}"


@tool
def get_time_filter_suggestion(time_range_days: int = 30) -> Dict[str, str]:
    """
    根据当前时间生成合理的日志查询时间范围建议
    
    Args:
        time_range_days: 建议的时间范围天数，默认30天
        
    Returns:
        Dict[str, str]: 时间过滤建议
    """
    try:
        current_time = datetime.now(timezone.utc)
        start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        suggestions = {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "today": {
                "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": "今日数据"
            },
            "last_7_days": {
                "start": (start_time - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
                "end": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": "最近7天"
            },
            "last_30_days": {
                "start": (start_time - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
                "end": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": "最近30天"
            },
            "custom_range": {
                "start": (start_time - timedelta(days=time_range_days)).strftime("%Y-%m-%d %H:%M:%S"),
                "end": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": f"最近{time_range_days}天"
            }
        }
        
        return suggestions
        
    except Exception as e:
        logger.error(f"生成时间过滤建议失败: {e}")
        return {"error": str(e)}