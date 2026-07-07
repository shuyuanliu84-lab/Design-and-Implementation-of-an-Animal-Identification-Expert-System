#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运行性能测试脚本
默认运行快速测试，使用 -f 参数运行完整测试
"""

import sys
from modules.knowledge_base import KnowledgeBase
from modules.working_memory import WorkingMemory
from modules.inference_engine import InferenceEngine
from modules.performance_tester import PerformanceTester

def main():
    # 检查参数
    run_full_test = "-f" in sys.argv or "--full" in sys.argv
    
    print("=" * 70)
    if run_full_test:
        print("🐾 大规模动物识别专家系统 - 完整性能测试")
    else:
        print("🐾 大规模动物识别专家系统 - 快速性能测试")
    print("=" * 70)
    
    if not run_full_test:
        print("\n💡 提示: 使用 -f 或 --full 参数运行完整详细测试")
        print("    快速测试仅测试核心性能：规则匹配和推理\n")
    
    # 初始化核心模块
    kb = KnowledgeBase("large_expert_system.db")
    wm = WorkingMemory()
    engine = InferenceEngine(kb, wm)
    
    # 运行性能测试
    tester = PerformanceTester("large_expert_system.db")
    if run_full_test:
        report = tester.run_full_test(engine)
    else:
        report = tester.run_fast_test(engine)
    
    print(report)
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
