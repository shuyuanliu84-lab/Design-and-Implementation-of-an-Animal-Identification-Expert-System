import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

class KnowledgeBase:
    def __init__(self, db_path: str = "expert_system.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建规则表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id INTEGER UNIQUE NOT NULL,
                    conditions TEXT NOT NULL,
                    conclusion TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建条件索引表（用于优化规则匹配）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rule_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id INTEGER NOT NULL,
                    condition_key TEXT NOT NULL,
                    condition_value TEXT NOT NULL,
                    FOREIGN KEY (rule_id) REFERENCES rules(rule_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_rule_id ON rules(rule_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_priority ON rules(priority)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conditions_key ON rule_conditions(condition_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conditions_rule ON rule_conditions(rule_id)')
            
            conn.commit()
    
    def add_rule(self, rule: Dict[str, Any]) -> str:
        """添加规则到知识库"""
        conditions = json.dumps(rule['conditions'])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # 插入规则
                cursor.execute('''
                    INSERT INTO rules (rule_id, conditions, conclusion, priority, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (rule['id'], conditions, rule['conclusion'], 
                      rule.get('priority', 1), rule.get('category', 'general')))
                
                # 插入条件索引
                for key, value in rule['conditions'].items():
                    cursor.execute('''
                        INSERT INTO rule_conditions (rule_id, condition_key, condition_value)
                        VALUES (?, ?, ?)
                    ''', (rule['id'], key, str(value)))
                
                conn.commit()
                return f"规则 {rule['id']} 添加成功"
            except sqlite3.IntegrityError:
                return f"规则 {rule['id']} 已存在"
    
    def remove_rule(self, rule_id: int) -> str:
        """从知识库中删除规则"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 先检查规则是否存在
            cursor.execute('SELECT COUNT(*) FROM rules WHERE rule_id = ?', (rule_id,))
            if cursor.fetchone()[0] == 0:
                return f"规则 {rule_id} 不存在"
            
            # 删除条件索引
            cursor.execute('DELETE FROM rule_conditions WHERE rule_id = ?', (rule_id,))
            
            # 删除规则
            cursor.execute('DELETE FROM rules WHERE rule_id = ?', (rule_id,))
            
            conn.commit()
            return f"规则 {rule_id} 删除成功"
    
    def update_rule(self, rule_id: int, new_rule: Dict[str, Any]) -> str:
        """更新知识库中的规则"""
        conditions = json.dumps(new_rule['conditions'])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 先检查规则是否存在
            cursor.execute('SELECT COUNT(*) FROM rules WHERE rule_id = ?', (rule_id,))
            if cursor.fetchone()[0] == 0:
                return f"规则 {rule_id} 不存在"
            
            # 更新规则
            cursor.execute('''
                UPDATE rules SET conditions = ?, conclusion = ?, priority = ?, 
                               category = ?, updated_at = CURRENT_TIMESTAMP
                WHERE rule_id = ?
            ''', (conditions, new_rule['conclusion'], 
                  new_rule.get('priority', 1), new_rule.get('category', 'general'), rule_id))
            
            # 删除旧条件索引
            cursor.execute('DELETE FROM rule_conditions WHERE rule_id = ?', (rule_id,))
            
            # 插入新条件索引
            for key, value in new_rule['conditions'].items():
                cursor.execute('''
                    INSERT INTO rule_conditions (rule_id, condition_key, condition_value)
                    VALUES (?, ?, ?)
                ''', (rule_id, key, str(value)))
            
            conn.commit()
            return f"规则 {rule_id} 更新成功"
    
    def get_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """获取单条规则"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT rule_id, conditions, conclusion, priority, category FROM rules WHERE rule_id = ?', (rule_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'conditions': json.loads(row[1]),
                    'conclusion': row[2],
                    'priority': row[3],
                    'category': row[4]
                }
            return None
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT rule_id, conditions, conclusion, priority, category FROM rules ORDER BY priority DESC, rule_id DESC')
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'conditions': json.loads(row[1]),
                    'conclusion': row[2],
                    'priority': row[3],
                    'category': row[4]
                }
                for row in rows
            ]
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别获取规则"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT rule_id, conditions, conclusion, priority, category FROM rules WHERE category = ? ORDER BY priority DESC', (category,))
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'conditions': json.loads(row[1]),
                    'conclusion': row[2],
                    'priority': row[3],
                    'category': row[4]
                }
                for row in rows
            ]
    
    def get_rules_by_condition(self, condition_key: str, condition_value: Any = None) -> List[Dict[str, Any]]:
        """根据条件查询相关规则（用于优化推理）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if condition_value is not None:
                cursor.execute('''
                    SELECT DISTINCT r.rule_id, r.conditions, r.conclusion, r.priority, r.category
                    FROM rules r
                    JOIN rule_conditions rc ON r.rule_id = rc.rule_id
                    WHERE rc.condition_key = ? AND rc.condition_value = ?
                    ORDER BY r.priority DESC
                ''', (condition_key, str(condition_value)))
            else:
                cursor.execute('''
                    SELECT DISTINCT r.rule_id, r.conditions, r.conclusion, r.priority, r.category
                    FROM rules r
                    JOIN rule_conditions rc ON r.rule_id = rc.rule_id
                    WHERE rc.condition_key = ?
                    ORDER BY r.priority DESC
                ''', (condition_key,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'conditions': json.loads(row[1]),
                    'conclusion': row[2],
                    'priority': row[3],
                    'category': row[4]
                }
                for row in rows
            ]
    
    def get_rule_count(self) -> int:
        """获取规则总数"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM rules')
            return cursor.fetchone()[0]
    
    def get_categories(self) -> List[str]:
        """获取所有规则类别"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM rules ORDER BY category')
            return [row[0] for row in cursor.fetchall()]
    
    def clear_all_rules(self) -> str:
        """清空所有规则"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM rule_conditions')
            cursor.execute('DELETE FROM rules')
            conn.commit()
            return "知识库已清空"
    
    def batch_add_rules(self, rules: List[Dict[str, Any]]) -> str:
        """批量添加规则"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            count = 0
            
            for rule in rules:
                try:
                    conditions = json.dumps(rule['conditions'])
                    cursor.execute('''
                        INSERT INTO rules (rule_id, conditions, conclusion, priority, category)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (rule['id'], conditions, rule['conclusion'], 
                          rule.get('priority', 1), rule.get('category', 'general')))
                    
                    for key, value in rule['conditions'].items():
                        cursor.execute('''
                            INSERT INTO rule_conditions (rule_id, condition_key, condition_value)
                            VALUES (?, ?, ?)
                        ''', (rule['id'], key, str(value)))
                    
                    count += 1
                except sqlite3.IntegrityError:
                    continue
            
            conn.commit()
            return f"批量添加完成，成功添加 {count} 条规则"

    def export_rules(self, file_path: str) -> str:
        """导出规则到JSON文件"""
        rules = self.get_all_rules()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        return f"规则已导出到 {file_path}"

    def import_rules(self, file_path: str) -> str:
        """从JSON文件导入规则"""
        if not os.path.exists(file_path):
            return f"文件 {file_path} 不存在"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        return self.batch_add_rules(rules)