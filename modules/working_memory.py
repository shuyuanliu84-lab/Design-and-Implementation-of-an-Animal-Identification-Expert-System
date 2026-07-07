from typing import Set, Tuple, List, Dict, Any
from collections import OrderedDict

class WorkingMemory:
    def __init__(self):
        self.facts: Set[Tuple[str, bool]] = set()
        self.fact_history: List[Dict[str, Any]] = []
        self.inference_history: List[str] = []
        self.fact_metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_fact(self, fact: str, value: bool = True, source: str = 'user') -> str:
        """添加事实到工作内存"""
        previous_value = self.get_fact_value(fact)
        
        if (fact, value) not in self.facts:
            self.facts.add((fact, value))
            
            # 记录历史
            self.fact_history.append({
                'action': 'add',
                'fact': fact,
                'value': value,
                'previous_value': previous_value,
                'source': source,
                'timestamp': len(self.fact_history)
            })
            
            # 添加元数据
            if fact not in self.fact_metadata:
                self.fact_metadata[fact] = {
                    'added_by': source,
                    'added_at': len(self.fact_history),
                    'inferred': source == 'inference'
                }
            
            return f"事实 '{fact}' = {'是' if value else '否'} 添加成功"
        return f"事实 '{fact}' = {'是' if value else '否'} 已存在"
    
    def remove_fact(self, fact: str) -> str:
        """从工作内存中移除事实"""
        for f, v in list(self.facts):
            if f == fact:
                self.facts.remove((f, v))
                
                self.fact_history.append({
                    'action': 'remove',
                    'fact': fact,
                    'value': v,
                    'previous_value': v,
                    'source': 'user',
                    'timestamp': len(self.fact_history)
                })
                
                if fact in self.fact_metadata:
                    del self.fact_metadata[fact]
                
                return f"事实 '{fact}' 已移除"
        return f"事实 '{fact}' 不存在"
    
    def update_fact(self, fact: str, value: bool) -> str:
        """更新事实的值"""
        old_value = self.get_fact_value(fact)
        
        if old_value is None:
            return self.add_fact(fact, value)
        
        if old_value != value:
            self.facts.discard((fact, old_value))
            self.facts.add((fact, value))
            
            self.fact_history.append({
                'action': 'update',
                'fact': fact,
                'value': value,
                'previous_value': old_value,
                'source': 'user',
                'timestamp': len(self.fact_history)
            })
            
            return f"事实 '{fact}' 已从 {'是' if old_value else '否'} 更新为 {'是' if value else '否'}"
        return f"事实 '{fact}' 已是 {'是' if value else '否'}"
    
    def get_fact_value(self, fact: str) -> bool:
        """获取事实的值"""
        for f, v in self.facts:
            if f == fact:
                return v
        return None
    
    def has_fact(self, fact: str, value: bool = True) -> bool:
        """检查事实是否存在"""
        return (fact, value) in self.facts
    
    def get_all_facts(self) -> Set[Tuple[str, bool]]:
        """获取所有事实"""
        return self.facts.copy()
    
    def get_facts_dict(self) -> Dict[str, bool]:
        """以字典形式获取所有事实"""
        return {fact: value for fact, value in self.facts}
    
    def get_fact_count(self) -> int:
        """获取事实数量"""
        return len(self.facts)
    
    def clear(self) -> str:
        """清空工作内存"""
        self.facts.clear()
        self.fact_metadata.clear()
        return "工作内存已清空"
    
    def clear_inference_history(self) -> None:
        """清空推理历史"""
        self.inference_history.clear()
    
    def add_inference_step(self, step: str) -> None:
        """添加推理步骤到历史"""
        self.inference_history.append(step)
    
    def get_inference_history(self) -> List[str]:
        """获取推理历史"""
        return self.inference_history.copy()
    
    def get_fact_history(self) -> List[Dict[str, Any]]:
        """获取事实变更历史"""
        return self.fact_history.copy()
    
    def get_fact_metadata(self, fact: str) -> Dict[str, Any]:
        """获取事实元数据"""
        return self.fact_metadata.get(fact, {})
    
    def get_inferred_facts(self) -> Set[str]:
        """获取所有推理得出的事实"""
        return {fact for fact, meta in self.fact_metadata.items() if meta.get('inferred', False)}
    
    def get_user_facts(self) -> Set[str]:
        """获取所有用户输入的事实"""
        return {fact for fact, meta in self.fact_metadata.items() if meta.get('added_by') == 'user'}
    
    def is_inferred(self, fact: str) -> bool:
        """检查事实是否是推理得出的"""
        return self.fact_metadata.get(fact, {}).get('inferred', False)
    
    def __contains__(self, item: Tuple[str, bool]) -> bool:
        """支持 in 操作符"""
        return item in self.facts