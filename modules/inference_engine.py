from typing import Set, Tuple, List, Dict, Any, Optional
from modules.knowledge_base import KnowledgeBase
from modules.working_memory import WorkingMemory
from modules.conflict_resolver import ConflictResolver
import time

class InferenceEngine:
    def __init__(self, knowledge_base: KnowledgeBase, working_memory: WorkingMemory, use_alpha_index: bool = True, use_beta_memory: bool = True):
        self.kb = knowledge_base
        self.wm = working_memory
        self.use_alpha_index = use_alpha_index
        self.use_beta_memory = use_beta_memory
        self.alpha_memory: Dict[str, Set[int]] = {}
        self.beta_memory: Dict[int, Dict[str, Any]] = {}
        self.conflict_resolver = ConflictResolver()
        self.runtime_conflicts: List[Dict[str, Any]] = []
        self.condition_check_count = 0
        self._build_alpha_index()
    
    def _build_alpha_index(self) -> None:
        """构建Alpha索引：条件键到规则的映射"""
        rules = self.kb.get_all_rules()
        self.alpha_memory.clear()
        
        for rule in rules:
            for condition_key in rule['conditions'].keys():
                if condition_key not in self.alpha_memory:
                    self.alpha_memory[condition_key] = set()
                self.alpha_memory[condition_key].add(rule['id'])
    
    def _update_alpha_index(self, rule_id: int, conditions: Dict[str, bool], remove: bool = False) -> None:
        """更新Alpha索引"""
        for condition_key in conditions.keys():
            if condition_key not in self.alpha_memory:
                self.alpha_memory[condition_key] = set()
            
            if remove:
                self.alpha_memory[condition_key].discard(rule_id)
            else:
                self.alpha_memory[condition_key].add(rule_id)
    
    def forward_chaining(self) -> Tuple[Set[str], List[str]]:
        """正向推理 - """
        self.wm.clear_inference_history()
        self.clear_beta_memory()
        self.runtime_conflicts.clear()
        self.condition_check_count = 0
        inferred_facts: Set[str] = set()
        fired_rules: List[Dict[str, Any]] = []
        changes = True
        cycle = 1
        
        start_time = time.time()
        
        while changes:
            changes = False
            self.wm.add_inference_step(f"\n══════════════════════════════════════")
            self.wm.add_inference_step(f"🔄 第 {cycle} 轮推理")
            self.wm.add_inference_step(f"══════════════════════════════════════")
            self.wm.add_inference_step(f"当前已知事实: {[f[0] for f in self.wm.get_all_facts()]}")
            
            # 获取可能匹配的规则（通过Alpha索引优化）
            candidate_rules = self._get_candidate_rules()
            
            for rule in candidate_rules:
                conclusion = rule['conclusion']
                
                # 跳过已经推断出结论的规则
                if self.wm.has_fact(conclusion):
                    continue
                
                # 检查规则的所有条件
                satisfied, satisfied_conditions, unsatisfied_conditions = self._check_rule_conditions(rule)
                
                # 记录检查过程（所有规则都记录）
                self.wm.add_inference_step(f"\n   ─ 规则 {rule['id']}: 如果 {', '.join(rule['conditions'].keys())}，则 {conclusion}")
                self.wm.add_inference_step(f"      条件检查: {len(satisfied_conditions)}/{len(rule['conditions'])} 满足")
                
                # 如果条件全部满足
                if satisfied and not self.wm.has_fact(conclusion):
                    self.wm.add_fact(conclusion, True, source='inference')
                    inferred_facts.add(conclusion)
                    fired_rules.append(rule)
                    
                    # 详细记录成功应用的规则
                    self.wm.add_inference_step(f"      ✅ 规则触发成功！")
                    self.wm.add_inference_step(f"         ├─ 已满足条件: {', '.join(satisfied_conditions)}")
                    self.wm.add_inference_step(f"         └─ 推断出新事实: {conclusion}")
                    
                    changes = True
            
            cycle += 1

        conflict = self.conflict_resolver.detect_runtime_conflict(
            fired_rules,
            self.wm.get_facts_dict()
        )
        if conflict:
            self.runtime_conflicts.append(conflict)
            if conflict['resolution'] == 'priority_winner':
                selected = set(conflict['selected_conclusions'])
                for conclusion in conflict['conflict_conclusions']:
                    if conclusion not in selected:
                        self.wm.remove_fact(conclusion)
                        inferred_facts.discard(conclusion)
            self.wm.add_inference_step("\n⚠️ 检测到互斥类别冲突")
            self.wm.add_inference_step(f"   冲突结论: {', '.join(conflict['conflict_conclusions'])}")
            self.wm.add_inference_step(f"   解决策略: {conflict['resolution']}")
            self.wm.add_inference_step(f"   采用结论: {', '.join(conflict['selected_conclusions'])}")
        
        inference_time = time.time() - start_time
        
        if cycle == 2:  # 只有一轮且没有变化
            self.wm.add_inference_step("\n📭 没有规则可以应用")
        
        # 总结推理结果
        if inferred_facts:
            self.wm.add_inference_step(f"\n══════════════════════════════════════")
            self.wm.add_inference_step(f"📊 推理完成，共推断出 {len(inferred_facts)} 个新事实")
            self.wm.add_inference_step(f"⏱️ 推理耗时: {inference_time:.4f} 秒")
            self.wm.add_inference_step(f"══════════════════════════════════════")
        
        return inferred_facts, self.wm.get_inference_history()
    
    def _get_candidate_rules(self) -> List[Dict[str, Any]]:
        """通过Alpha索引获取可能匹配的规则"""
        if not self.use_alpha_index:
            return self.kb.get_all_rules()

        facts = self.wm.get_all_facts()
        candidate_rule_ids: Set[int] = set()
        
        for fact, value in facts:
            if fact in self.alpha_memory:
                candidate_rule_ids.update(self.alpha_memory[fact])
        
        # 如果没有Alpha索引（无索引模式），遍历所有规则
        if not self.alpha_memory or len(candidate_rule_ids) == 0:
            return self.kb.get_all_rules()
        
        # 获取规则详情并按优先级排序
        rules = []
        for rule_id in candidate_rule_ids:
            rule = self.kb.get_rule(rule_id)
            if rule:
                rules.append(rule)
        
        # 按优先级降序、规则ID升序排序
        rules.sort(key=lambda r: (-r['priority'], r['id']))
        return rules
    
    def _check_rule_conditions(self, rule: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """检查规则的所有条件是否满足"""
        if self.use_beta_memory:
            return self._check_rule_conditions_with_beta(rule)

        satisfied_conditions = []
        unsatisfied_conditions = []
        
        for condition_key, condition_value in rule['conditions'].items():
            self.condition_check_count += 1
            if self.wm.has_fact(condition_key, condition_value):
                satisfied_conditions.append(condition_key)
            else:
                unsatisfied_conditions.append(condition_key)
        
        return (len(unsatisfied_conditions) == 0, satisfied_conditions, unsatisfied_conditions)

    def _check_rule_conditions_with_beta(self, rule: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """使用Beta记忆复用规则的部分匹配状态。"""
        facts = self.wm.get_facts_dict()
        rule_id = rule['id']
        cache = self.beta_memory.get(rule_id, {
            'matched': set(),
            'unmatched': set(rule['conditions'].keys()),
            'fact_snapshot': {}
        })

        matched = set(cache['matched'])
        unmatched = set(cache['unmatched'])
        snapshot = dict(cache.get('fact_snapshot', {}))

        for condition_key, condition_value in rule['conditions'].items():
            current_value = facts.get(condition_key)
            if snapshot.get(condition_key, object()) == current_value:
                continue

            self.condition_check_count += 1
            snapshot[condition_key] = current_value
            if current_value == condition_value:
                matched.add(condition_key)
                unmatched.discard(condition_key)
            else:
                matched.discard(condition_key)
                unmatched.add(condition_key)

        self.beta_memory[rule_id] = {
            'matched': matched,
            'unmatched': unmatched,
            'fact_snapshot': snapshot,
            'progress': len(matched) / len(rule['conditions']) if rule['conditions'] else 1.0
        }
        return (len(unmatched) == 0, sorted(matched), sorted(unmatched))
    
    def backward_chaining(self, target: str, ask_user_callback=None) -> Tuple[bool, List[str]]:
        """反向推理"""
        self.wm.clear_inference_history()
        result = self._backward_chaining_recursive(target, ask_user_callback)
        return result, self.wm.get_inference_history()
    
    def _backward_chaining_recursive(self, target: str, ask_user_callback=None) -> bool:
        """反向推理递归函数"""
        # 检查目标是否已在工作内存中
        if self.wm.has_fact(target):
            self.wm.add_inference_step(f"✓ 目标 {target} 已在工作内存中")
            return True
        
        # 查找能推导出目标的规则（按优先级排序）
        rules = self.kb.get_rules_by_condition(target)
        # 过滤出结论为目标的规则
        target_rules = [r for r in rules if r['conclusion'] == target]
        
        if not target_rules:
            # 如果没有直接规则，尝试从所有规则中查找
            all_rules = self.kb.get_all_rules()
            target_rules = [r for r in all_rules if r['conclusion'] == target]
        
        # 按优先级排序
        target_rules.sort(key=lambda r: -r['priority'])
        
        for rule in target_rules:
            self.wm.add_inference_step(f"🔍 尝试规则 {rule['id']} 推导 {target}")
            self.wm.add_inference_step(f"   规则描述: 如果 {', '.join(rule['conditions'].keys())}，则 {target}")
            
            all_conditions_met = True
            for condition, value in rule['conditions'].items():
                if not self.wm.has_fact(condition, value):
                    # 询问用户或递归检查条件
                    if ask_user_callback:
                        user_response = ask_user_callback(condition)
                        if user_response:
                            self.wm.add_fact(condition, True, source='user')
                            self.wm.add_inference_step(f"   ├─ 用户确认: {condition} = 是")
                        else:
                            self.wm.add_inference_step(f"   ├─ 用户否定: {condition} = 否")
                            all_conditions_met = False
                            break
                    else:
                        self.wm.add_inference_step(f"   ├─ 需要验证条件: {condition}")
                        if not self._backward_chaining_recursive(condition, ask_user_callback):
                            all_conditions_met = False
                            break
            
            if all_conditions_met:
                self.wm.add_fact(target, True, source='inference')
                self.wm.add_inference_step(f"   └─ ✅ 规则满足，推断出 {target}")
                return True
        
        self.wm.add_inference_step(f"❌ 无法推导 {target}")
        return False
    
    def refresh_index(self) -> None:
        """刷新Alpha索引（当知识库发生变化时调用）"""
        self._build_alpha_index()
        self.clear_beta_memory()

    def clear_beta_memory(self) -> None:
        """清空Beta网络部分匹配记忆。"""
        self.beta_memory.clear()

    def get_runtime_conflicts(self) -> List[Dict[str, Any]]:
        """获取最近一次推理产生的运行时冲突。"""
        return list(self.runtime_conflicts)
    
    def get_rule_matching_stats(self) -> Dict[str, Any]:
        """获取规则匹配统计信息"""
        total_rules = self.kb.get_rule_count()
        indexed_conditions = len(self.alpha_memory)
        
        return {
            'total_rules': total_rules,
            'indexed_conditions': indexed_conditions,
            'avg_rules_per_condition': sum(len(ids) for ids in self.alpha_memory.values()) / indexed_conditions if indexed_conditions > 0 else 0,
            'beta_memory_entries': len(self.beta_memory),
            'condition_check_count': self.condition_check_count
        }
