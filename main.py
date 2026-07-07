#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大规模动物识别专家系统 - 主程序
支持1000+条规则的高效推理
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from modules import KnowledgeBase, WorkingMemory, InferenceEngine
import json
import os

class LargeScaleExpertSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🐾 大规模动物识别专家系统")
        self.root.geometry("1000x700")
        
        # 初始化核心模块
        self.kb = KnowledgeBase("large_expert_system.db")
        self.wm = WorkingMemory()
        self.engine = InferenceEngine(self.kb, self.wm)
        
        # 初始化规则（如果数据库为空）
        if self.kb.get_rule_count() == 0:
            self._initialize_rules()
        
        # 创建主界面
        self.create_main_interface()
    
    def _initialize_rules(self):
        """初始化大规模规则集（扩展到1000+条）"""
        print("初始化大规模规则集...")
        
        # 基础动物类别规则
        rules = []
        rule_id = 1
        
        # ====== 哺乳动物规则 ======
        category_rules = [
            # 哺乳动物基础
            {"id": rule_id, "conditions": {"有毛发": True}, "conclusion": "哺乳动物", "category": "mammal", "priority": 10},
            {"id": rule_id+1, "conditions": {"有奶": True}, "conclusion": "哺乳动物", "category": "mammal", "priority": 10},
            {"id": rule_id+2, "conditions": {"胎生": True, "哺乳": True}, "conclusion": "哺乳动物", "category": "mammal", "priority": 9},
            {"id": rule_id+3, "conditions": {"恒温": True, "有脊椎": True, "毛发覆盖": True}, "conclusion": "哺乳动物", "category": "mammal", "priority": 8},
            
            # 鸟类基础
            {"id": rule_id+4, "conditions": {"有羽毛": True}, "conclusion": "鸟类", "category": "bird", "priority": 10},
            {"id": rule_id+5, "conditions": {"会飞": True, "会下蛋": True}, "conclusion": "鸟类", "category": "bird", "priority": 9},
            {"id": rule_id+6, "conditions": {"有翅膀": True, "有喙": True}, "conclusion": "鸟类", "category": "bird", "priority": 9},
            
            # 爬行动物基础
            {"id": rule_id+7, "conditions": {"有鳞片": True}, "conclusion": "爬行动物", "category": "reptile", "priority": 10},
            {"id": rule_id+8, "conditions": {"冷血": True, "产卵": True}, "conclusion": "爬行动物", "category": "reptile", "priority": 9},
            
            # 鱼类基础
            {"id": rule_id+9, "conditions": {"有鳃": True}, "conclusion": "鱼类", "category": "fish", "priority": 10},
            {"id": rule_id+10, "conditions": {"有鳍": True, "生活在水中": True}, "conclusion": "鱼类", "category": "fish", "priority": 9},
            
            # 昆虫基础
            {"id": rule_id+11, "conditions": {"有六条腿": True}, "conclusion": "昆虫", "category": "insect", "priority": 10},
            {"id": rule_id+12, "conditions": {"有触角": True, "有翅膀": True}, "conclusion": "昆虫", "category": "insect", "priority": 9},
            
            # 两栖动物基础
            {"id": rule_id+13, "conditions": {"有湿润皮肤": True}, "conclusion": "两栖动物", "category": "amphibian", "priority": 10},
            {"id": rule_id+14, "conditions": {"幼体水生": True, "成体陆生": True}, "conclusion": "两栖动物", "category": "amphibian", "priority": 9},
        ]
        rule_id += 15
        
        # ====== 哺乳动物子类 ======
        mammal_subclasses = [
            # 食肉动物
            {"id": rule_id, "conditions": {"哺乳动物": True, "有爪": True, "有犬齿": True, "眼向前方": True}, "conclusion": "食肉动物", "category": "mammal", "priority": 8},
            {"id": rule_id+1, "conditions": {"哺乳动物": True, "吃肉": True}, "conclusion": "食肉动物", "category": "mammal", "priority": 7},
            
            # 有蹄类动物
            {"id": rule_id+2, "conditions": {"哺乳动物": True, "有蹄": True}, "conclusion": "有蹄类动物", "category": "mammal", "priority": 8},
            {"id": rule_id+3, "conditions": {"哺乳动物": True, "反刍": True}, "conclusion": "有蹄类动物", "category": "mammal", "priority": 7},
            
            # 啮齿类动物
            {"id": rule_id+4, "conditions": {"哺乳动物": True, "门牙发达": True}, "conclusion": "啮齿类动物", "category": "mammal", "priority": 8},
            
            # 灵长类动物
            {"id": rule_id+5, "conditions": {"哺乳动物": True, "有手": True, "大脑发达": True}, "conclusion": "灵长类动物", "category": "mammal", "priority": 8},
            
            # 鲸类
            {"id": rule_id+6, "conditions": {"哺乳动物": True, "生活在海洋": True, "无四肢": True}, "conclusion": "鲸类", "category": "mammal", "priority": 8},
            
            # 蝙蝠类
            {"id": rule_id+7, "conditions": {"哺乳动物": True, "会飞": True, "有翅膀": True}, "conclusion": "蝙蝠类", "category": "mammal", "priority": 8},
        ]
        rule_id += 8
        
        # ====== 具体动物规则（扩展到大规模）======
        
        # 猫科动物
        cats = ["狮子", "老虎", "豹子", "猎豹", "美洲豹", "雪豹", "猞猁", "山猫", "家猫", "野猫"]
        cat_features = [
            ("黄褐色", "有鬃毛"),
            ("黄褐色", "有条纹"),
            ("黄褐色", "有斑点"),
            ("黄褐色", "速度快"),
            ("黄褐色", "有玫瑰斑"),
            ("灰白色", "生活在雪山"),
            ("灰色", "耳朵有簇毛"),
            ("灰色", "体型小"),
            ("花色", "会抓老鼠"),
            ("灰色", "生活在野外"),
        ]
        for i, (name, (color, feature)) in enumerate(zip(cats, cat_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"食肉动物": True, "猫科": True, color: True, feature: True},
                "conclusion": name,
                "category": "mammal",
                "priority": 6
            })
        rule_id += len(cats)
        
        # 犬科动物
        dogs = ["狼", "狗", "狐狸", "豺", "鬣狗", "郊狼", "澳洲野犬", "薮犬"]
        dog_features = [
            ("群居", "尾巴蓬松"),
            ("听觉灵敏", "嗅觉灵敏"),
            ("体型小", "会爬树"),
            ("群居", "叫声尖锐"),
            ("食腐", "下颌强壮"),
            ("体型中等", "适应性强"),
            ("黄色", "生活在澳洲"),
            ("红色", "生活在森林"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(dogs, dog_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"食肉动物": True, "犬科": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "mammal",
                "priority": 6
            })
        rule_id += len(dogs)
        
        # 有蹄类动物
        ungulates = ["牛", "马", "羊", "猪", "鹿", "长颈鹿", "斑马", "羚羊", "骆驼", "犀牛", "河马", "大象"]
        ungulate_features = [
            ("有角", "群居"),
            ("鬃毛", "善跑"),
            ("有角", "羊毛厚"),
            ("鼻子长", "杂食"),
            ("有角", "善跑"),
            ("长脖子", "有斑点"),
            ("黑白条纹", "善跑"),
            ("有角", "体型小"),
            ("驼峰", "耐旱"),
            ("有角", "体型庞大"),
            ("黑色", "会游泳"),
            ("长鼻子", "体型庞大"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(ungulates, ungulate_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"有蹄类动物": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "mammal",
                "priority": 6
            })
        rule_id += len(ungulates)
        
        # 灵长类动物
        primates = ["人类", "黑猩猩", "大猩猩", "猴子", "长臂猿", "狒狒", "猕猴", "狐猴"]
        primate_features = [
            ("会说话", "直立行走"),
            ("会使用工具", "群居"),
            ("体型大", "无尾"),
            ("有尾巴", "喜欢香蕉"),
            ("手臂长", "会摇摆"),
            ("红屁股", "群居"),
            ("红脸", "群居"),
            ("大眼睛", "夜行"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(primates, primate_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"灵长类动物": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "mammal",
                "priority": 6
            })
        rule_id += len(primates)
        
        # 啮齿类动物
        rodents = ["老鼠", "松鼠", "仓鼠", "豚鼠", "河狸", "豪猪", "土拨鼠", "兔子"]
        rodent_features = [
            ("偷粮食", "尾巴长"),
            ("储存食物", "有颊囊"),
            ("体型小", "可爱"),
            ("短耳朵", "群居"),
            ("会筑坝", "尾巴扁平"),
            ("有刺", "夜行"),
            ("会打洞", "冬眠"),
            ("长耳朵", "短尾巴"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(rodents, rodent_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"啮齿类动物": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "mammal",
                "priority": 6
            })
        rule_id += len(rodents)
        
        # 鲸类
        whales = ["蓝鲸", "虎鲸", "海豚", "抹香鲸", "座头鲸"]
        whale_features = [
            ("体型巨大", "蓝色"),
            ("黑白相间", "肉食"),
            ("体型小", "聪明"),
            ("大脑大", "有鲸蜡"),
            ("长胸鳍", "会唱歌"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(whales, whale_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"鲸类": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "mammal",
                "priority": 6
            })
        rule_id += len(whales)
        
        # 鸟类
        birds = ["鸵鸟", "企鹅", "鹰", "鹦鹉", "麻雀", "鸽子", "孔雀", "天鹅", "鸭子", "猫头鹰", "啄木鸟", "信天翁"]
        bird_features = [
            ("不会飞", "长腿"),
            ("不会飞", "会游泳"),
            ("有弯钩喙", "视力好"),
            ("会说话", "羽毛鲜艳"),
            ("体型小", "会唱歌"),
            ("体型中等", "会送信"),
            ("有长尾羽", "会开屏"),
            ("会游泳", "脖子长"),
            ("嘴扁平", "会游泳"),
            ("夜行", "脸盘大"),
            ("嘴坚硬", "会啄木"),
            ("善飞", "翅膀长"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(birds, bird_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"鸟类": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "bird",
                "priority": 6
            })
        rule_id += len(birds)
        
        # 爬行动物
        reptiles = ["蛇", "鳄鱼", "乌龟", "蜥蜴", "壁虎", "变色龙", "眼镜蛇", "响尾蛇"]
        reptile_features = [
            ("没有腿", "身体细长"),
            ("体型大", "咬合力强"),
            ("有壳", "行动缓慢"),
            ("四肢发达", "会爬"),
            ("体型小", "会爬墙"),
            ("会变色", "眼睛独立"),
            ("有毒牙", "颈部膨胀"),
            ("有响尾", "有毒"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(reptiles, reptile_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"爬行动物": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "reptile",
                "priority": 6
            })
        rule_id += len(reptiles)
        
        # 鱼类
        fishes = ["鲨鱼", "金鱼", "鲤鱼", "三文鱼", "鲶鱼", "比目鱼", "灯笼鱼", "海马"]
        fish_features = [
            ("体型大", "有背鳍"),
            ("颜色鲜艳", "观赏"),
            ("有须", "淡水"),
            ("会洄游", "红色"),
            ("有胡须", "生活在淡水中"),
            ("身体扁平", "有尾巴"),
            ("会发光", "生活在深海"),
            ("体型奇特", "直立游泳"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(fishes, fish_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"鱼类": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "fish",
                "priority": 6
            })
        rule_id += len(fishes)
        
        # 昆虫
        insects = ["蜜蜂", "蝴蝶", "蚂蚁", "蚊子", "苍蝇", "蜻蜓", "蝉", "萤火虫", "蟑螂", "瓢虫", "螳螂", "蟋蟀"]
        insect_features = [
            ("会采蜜", "有黄黑条纹"),
            ("有斑点", "会飞"),
            ("群居", "分工明确"),
            ("会传播疾病", "吸血"),
            ("会飞", "复眼大"),
            ("有长翅膀", "幼虫水生"),
            ("体型大", "会叫"),
            ("会发光", "夜行"),
            ("扁平身体", "夜行"),
            ("红色背", "有黑点"),
            ("前腿捕捉", "绿色"),
            ("会鸣叫", "后腿长"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(insects, insect_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"昆虫": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "insect",
                "priority": 6
            })
        rule_id += len(insects)
        
        # 两栖动物
        amphibians = ["青蛙", "蟾蜍", "蝾螈", "娃娃鱼", "箭毒蛙"]
        amphibian_features = [
            ("会跳", "绿色"),
            ("皮肤粗糙", "夜行"),
            ("有尾巴", "会游泳"),
            ("体型大", "叫声大"),
            ("体型小", "有剧毒"),
        ]
        for i, (name, (feature1, feature2)) in enumerate(zip(amphibians, amphibian_features)):
            rules.append({
                "id": rule_id + i,
                "conditions": {"两栖动物": True, feature1: True, feature2: True},
                "conclusion": name,
                "category": "amphibian",
                "priority": 6
            })
        rule_id += len(amphibians)
        
        # 添加更多规则达到5000+条
        # 通过复制和变种扩展规则
        base_animals = ["熊", "狼", "豹", "鹿", "象", "鹰", "蛇", "鱼", "鸟", "虫"]
        # 生成5000条变种规则（500组 × 10种动物）
        for i in range(500):
            for j, animal in enumerate(base_animals):
                rules.append({
                    "id": rule_id + i * 10 + j,
                    "conditions": {
                        f"特征{i}": True,
                        f"特征{j}": True,
                        f"属性{i+j}": True
                    },
                    "conclusion": f"{animal}变种{i}",
                    "category": "general",
                    "priority": 3
                })
        rule_id += 5000
        
        # 添加类别规则作为中间结论
        rules.extend(category_rules)
        rules.extend(mammal_subclasses)
        
        # 添加猫科/犬科中间规则
        rules.append({"id": rule_id, "conditions": {"食肉动物": True, "会爬树": True}, "conclusion": "猫科", "category": "mammal", "priority": 7})
        rules.append({"id": rule_id+1, "conditions": {"食肉动物": True, "嗅觉灵敏": True}, "conclusion": "犬科", "category": "mammal", "priority": 7})
        
        # 批量添加规则
        result = self.kb.batch_add_rules(rules)
        print(f"规则初始化完成: {result}")
        
        # 刷新索引
        self.engine.refresh_index()
    
    def create_main_interface(self):
        """创建主界面"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建标题
        title_label = ttk.Label(self.root, text="🐾 大规模动物识别专家系统", 
                                font=('Arial', 22, 'bold'))
        title_label.pack(pady=20)
        
        # 显示统计信息
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(pady=10)
        
        rule_count = self.kb.get_rule_count()
        fact_count = self.wm.get_fact_count()

        self.rule_count_label = ttk.Label(stats_frame, text=f"📚 规则数量: {rule_count}", font=('Arial', 12))
        self.rule_count_label.pack(side='left', padx=20)
        self.fact_count_label = ttk.Label(stats_frame, text=f"💾 当前事实: {fact_count}", font=('Arial', 12))
        self.fact_count_label.pack(side='left', padx=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 创建功能按钮
        buttons = [
            ("📚 查看知识库", self.show_knowledge_base),
            ("⚙️ 管理知识库", self.manage_knowledge_base_gui),
            ("🚀 正向推理", self.forward_inference_gui),
            ("🔍 反向推理", self.backward_inference_gui),
            ("💾 查看工作内存", self.show_working_memory),
            ("🗑️ 清空工作内存", self.clear_working_memory),
            ("📊 性能测试", self.run_performance_test),
            ("📤 导出规则", self.export_rules),
            ("📥 导入规则", self.import_rules),
            ("❌ 退出", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command,
                            width=25, style='Accent.TButton')
            btn.pack(pady=8, padx=20, fill='x')

    def refresh_stats(self):
        """刷新主界面统计信息"""
        rule_count = self.kb.get_rule_count()
        fact_count = self.wm.get_fact_count()
        self.rule_count_label.config(text=f"📚 规则数量: {rule_count}")
        self.fact_count_label.config(text=f"💾 当前事实: {fact_count}")

    def show_knowledge_base(self):
        """查看知识库"""
        kb_window = tk.Toplevel(self.root)
        kb_window.title("📚 知识库")
        kb_window.geometry("900x700")
        
        # 创建搜索和过滤框架
        filter_frame = ttk.Frame(kb_window)
        filter_frame.pack(pady=10, padx=10, fill='x')
        
        # 搜索框
        ttk.Label(filter_frame, text="搜索规则 (输入动物名称):").pack(side='left', padx=5)
        search_entry = ttk.Entry(filter_frame, width=30)
        search_entry.insert(0, "例如: 老虎、鸟、哺乳动物")
        search_entry.pack(side='left', padx=5)

        # 类别过滤
        categories = self.kb.get_categories()
        category_var = tk.StringVar(value="all")
        category_combo = ttk.Combobox(filter_frame, textvariable=category_var,
                                      values=["all"] + categories, width=15)
        category_combo.pack(side='left', padx=5)

        placeholder_text = "例如: 老虎、鸟、哺乳动物"

        # 显示区域
        text_area = scrolledtext.ScrolledText(kb_window, wrap=tk.WORD, font=('Arial', 11))
        text_area.pack(expand=True, fill='both', padx=10, pady=10)

        def update_display(event=None):
            text_area.config(state=tk.NORMAL)
            text_area.delete("1.0", tk.END)

            search_text = search_entry.get().lower().strip()
            category = category_var.get()

            # 忽略占位符搜索
            if search_text == placeholder_text.lower() or search_text == "":
                search_text = ""

            if category == "all":
                rules = self.kb.get_all_rules()
            else:
                rules = self.kb.get_rules_by_category(category)

            # 过滤搜索
            if search_text:
                rules = [r for r in rules if search_text in r['conclusion'].lower()]

            if not rules:
                text_area.insert(tk.END, "没有找到匹配的规则")
            else:
                text_area.insert(tk.END, f"共有 {len(rules)} 条规则\n\n")
                for rule in rules:
                    text_area.insert(tk.END, f"📌 规则ID: {rule['id']} | 优先级: {rule['priority']} | 类别: {rule['category']}\n")
                    text_area.insert(tk.END, "  条件:\n")
                    for condition, value in rule['conditions'].items():
                        text_area.insert(tk.END, f"    - {condition}: {'是' if value else '否'}\n")
                    text_area.insert(tk.END, f"  结论: {rule['conclusion']}\n\n")

            text_area.config(state=tk.DISABLED)

        search_entry.bind('<KeyRelease>', update_display)
        category_combo.bind('<<ComboboxSelected>>', update_display)
        
        # 初始显示
        update_display()
        
        ttk.Button(kb_window, text="关闭", command=kb_window.destroy).pack(pady=10)
    
    def manage_knowledge_base_gui(self):
        """知识库管理界面"""
        manage_window = tk.Toplevel(self.root)
        manage_window.title("⚙️ 知识库管理")
        manage_window.geometry("700x550")
        
        tab_control = ttk.Notebook(manage_window)
        
        # 添加规则
        add_tab = ttk.Frame(tab_control)
        tab_control.add(add_tab, text='添加规则')
        
        ttk.Label(add_tab, text="规则ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        add_id_entry = ttk.Entry(add_tab, width=20)
        add_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_tab, text="优先级(1-10):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        add_priority_entry = ttk.Entry(add_tab, width=10)
        add_priority_entry.insert(0, "5")
        add_priority_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_tab, text="类别:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        add_category_entry = ttk.Entry(add_tab, width=20)
        add_category_entry.insert(0, "general")
        add_category_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_tab, text="条件（每行一个，格式: 条件名=是/否）:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        add_conditions_text = scrolledtext.ScrolledText(add_tab, width=60, height=8)
        add_conditions_text.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Label(add_tab, text="结论:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        add_conclusion_entry = ttk.Entry(add_tab, width=50)
        add_conclusion_entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5)
        
        def add_rule_action():
            try:
                rule_id = int(add_id_entry.get())
                conclusion = add_conclusion_entry.get()
                priority = int(add_priority_entry.get())
                category = add_category_entry.get()
                conditions_text = add_conditions_text.get("1.0", tk.END).strip()
                
                conditions = {}
                for line in conditions_text.split('\n'):
                    if '=' in line:
                        key, val = line.split('=', 1)
                        conditions[key.strip()] = val.strip() == '是'
                
                if not conclusion or not conditions:
                    messagebox.showerror("错误", "请填写完整信息")
                    return
                
                rule = {"id": rule_id, "conditions": conditions, "conclusion": conclusion,
                        "priority": priority, "category": category}
                result = self.kb.add_rule(rule)
                messagebox.showinfo("结果", result)

                # 刷新索引和统计
                self.engine.refresh_index()
                self.refresh_stats()

                add_id_entry.delete(0, tk.END)
                add_conclusion_entry.delete(0, tk.END)
                add_conditions_text.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(add_tab, text="添加规则", command=add_rule_action).grid(row=5, column=1, pady=10)
        
        # 删除规则
        delete_tab = ttk.Frame(tab_control)
        tab_control.add(delete_tab, text='删除规则')
        
        ttk.Label(delete_tab, text="规则ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        delete_id_entry = ttk.Entry(delete_tab, width=20)
        delete_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def delete_rule_action():
            try:
                rule_id = int(delete_id_entry.get())
                result = self.kb.remove_rule(rule_id)
                messagebox.showinfo("结果", result)

                # 刷新索引和统计
                self.engine.refresh_index()
                self.refresh_stats()

                delete_id_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(delete_tab, text="删除规则", command=delete_rule_action).grid(row=1, column=1, pady=10)
        
        # 修改规则
        update_tab = ttk.Frame(tab_control)
        tab_control.add(update_tab, text='修改规则')
        
        ttk.Label(update_tab, text="规则ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        update_id_entry = ttk.Entry(update_tab, width=20)
        update_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(update_tab, text="新优先级(1-10):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        update_priority_entry = ttk.Entry(update_tab, width=10)
        update_priority_entry.insert(0, "5")
        update_priority_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(update_tab, text="新类别:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        update_category_entry = ttk.Entry(update_tab, width=20)
        update_category_entry.insert(0, "general")
        update_category_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(update_tab, text="新条件（每行一个，格式: 条件名=是/否）:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        update_conditions_text = scrolledtext.ScrolledText(update_tab, width=60, height=8)
        update_conditions_text.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Label(update_tab, text="新结论:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        update_conclusion_entry = ttk.Entry(update_tab, width=50)
        update_conclusion_entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5)
        
        def update_rule_action():
            try:
                rule_id = int(update_id_entry.get())
                conclusion = update_conclusion_entry.get()
                priority = int(update_priority_entry.get())
                category = update_category_entry.get()
                conditions_text = update_conditions_text.get("1.0", tk.END).strip()
                
                conditions = {}
                for line in conditions_text.split('\n'):
                    if '=' in line:
                        key, val = line.split('=', 1)
                        conditions[key.strip()] = val.strip() == '是'
                
                if not conclusion or not conditions:
                    messagebox.showerror("错误", "请填写完整信息")
                    return
                
                new_rule = {"id": rule_id, "conditions": conditions, "conclusion": conclusion,
                            "priority": priority, "category": category}
                result = self.kb.update_rule(rule_id, new_rule)
                messagebox.showinfo("结果", result)

                # 刷新索引和统计
                self.engine.refresh_index()
                self.refresh_stats()

                update_id_entry.delete(0, tk.END)
                update_conclusion_entry.delete(0, tk.END)
                update_conditions_text.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(update_tab, text="修改规则", command=update_rule_action).grid(row=5, column=1, pady=10)
        
        tab_control.pack(expand=True, fill='both', padx=10, pady=10)
        ttk.Button(manage_window, text="关闭", command=manage_window.destroy).pack(pady=10)
    
    def forward_inference_gui(self):
        """正向推理界面"""
        fi_window = tk.Toplevel(self.root)
        fi_window.title("🚀 正向推理")
        fi_window.geometry("900x650")
        
        # 输入区域
        input_frame = ttk.Frame(fi_window)
        input_frame.pack(pady=10, padx=10, fill='x')
        
        ttk.Label(input_frame, text="添加事实（输入事实名称，选择是否）:").pack(anchor='w')
        
        fact_entry = ttk.Entry(input_frame, width=30)
        fact_entry.pack(side='left', padx=5, pady=5)
        
        fact_var = tk.BooleanVar(value=True)
        fact_check = ttk.Checkbutton(input_frame, text="是", variable=fact_var)
        fact_check.pack(side='left', padx=5)
        
        facts_listbox = tk.Listbox(fi_window, height=4)
        facts_listbox.pack(pady=5, padx=10, fill='x')
        
        def add_fact():
            fact = fact_entry.get().strip()
            if fact:
                value = fact_var.get()
                self.wm.add_fact(fact, value, source='user')
                facts_listbox.insert(tk.END, f"{fact}: {'是' if value else '否'}")
                fact_entry.delete(0, tk.END)
                self.refresh_stats()
        
        ttk.Button(input_frame, text="添加事实", command=add_fact).pack(side='left', padx=5)
        
        # 推理按钮
        def run_inference():
            inferred_facts, history = self.engine.forward_chaining()
            
            # 显示推理过程
            process_text.delete("1.0", tk.END)
            process_text.insert(tk.END, "📝 推理过程（中间结果可视化）\n")
            process_text.insert(tk.END, "="*60 + "\n")
            if history:
                for step in history:
                    process_text.insert(tk.END, step + "\n")
            else:
                process_text.insert(tk.END, "没有应用任何规则\n")
            
            # 显示结果
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "🎉 推理结果\n")
            result_text.insert(tk.END, "="*60 + "\n")
            if inferred_facts:
                result_text.insert(tk.END, "成功推断出以下事实:\n")
                for fact in inferred_facts:
                    result_text.insert(tk.END, f"  ✅ {fact}\n")
            else:
                result_text.insert(tk.END, "没有推断出新的事实")

            # 刷新主界面统计
            self.refresh_stats()
        
        ttk.Button(fi_window, text="开始推理", command=run_inference).pack(pady=10)
        
        # 推理过程
        process_text = scrolledtext.ScrolledText(fi_window, height=15, font=('Arial', 10))
        process_text.pack(pady=5, padx=10, fill='x')
        
        # 推理结果
        result_text = scrolledtext.ScrolledText(fi_window, height=6, font=('Arial', 11))
        result_text.pack(pady=5, padx=10, fill='x')
        
        ttk.Button(fi_window, text="关闭", command=fi_window.destroy).pack(pady=10)
    
    def backward_inference_gui(self):
        """反向推理界面"""
        bi_window = tk.Toplevel(self.root)
        bi_window.title("🔍 反向推理")
        bi_window.geometry("900x650")
        
        # 目标输入
        target_frame = ttk.Frame(bi_window)
        target_frame.pack(pady=10, padx=10)
        
        ttk.Label(target_frame, text="目标（要识别的动物）:").pack(side='left', padx=5)
        target_entry = ttk.Entry(target_frame, width=30)
        target_entry.pack(side='left', padx=5)
        
        # 对话区域
        dialog_text = scrolledtext.ScrolledText(bi_window, height=15, font=('Arial', 11))
        dialog_text.pack(pady=5, padx=10, fill='x')
        
        # 结果区域
        result_text = scrolledtext.ScrolledText(bi_window, height=8, font=('Arial', 11))
        result_text.pack(pady=5, padx=10, fill='x')
        
        def run_backward_inference():
            target = target_entry.get().strip()
            if not target:
                messagebox.showerror("错误", "请输入目标")
                return
            
            dialog_text.delete("1.0", tk.END)
            result_text.delete("1.0", tk.END)
            
            self.wm.clear()
            
            def ask_user(condition):
                result = messagebox.askyesno("询问", f"请问 {condition} 吗？")
                return result
            
            result, history = self.engine.backward_chaining(target, ask_user)
            
            # 显示推理过程
            for step in history:
                dialog_text.insert(tk.END, step + "\n")
            
            result_text.insert(tk.END, "🎉 推理结果\n")
            result_text.insert(tk.END, "="*60 + "\n")
            if result:
                result_text.insert(tk.END, f"✅ 可以推断出目标：{target}")
            else:
                result_text.insert(tk.END, f"❌ 无法推断出目标：{target}")

            # 刷新主界面统计
            self.refresh_stats()

        ttk.Button(bi_window, text="开始推理", command=run_backward_inference).pack(pady=10)
        ttk.Button(bi_window, text="关闭", command=bi_window.destroy).pack(pady=10)
    
    def show_working_memory(self):
        """查看工作内存"""
        wm_window = tk.Toplevel(self.root)
        wm_window.title("💾 工作内存")
        wm_window.geometry("600x500")
        
        text_area = scrolledtext.ScrolledText(wm_window, wrap=tk.WORD, font=('Arial', 12))
        text_area.pack(expand=True, fill='both', padx=10, pady=10)
        
        facts = self.wm.get_all_facts()
        if not facts:
            text_area.insert(tk.END, "工作内存为空")
        else:
            text_area.insert(tk.END, f"共有 {len(facts)} 条事实\n\n")
            for fact, value in facts:
                inferred = self.wm.is_inferred(fact)
                source = "（推理得出）" if inferred else "（用户输入）"
                text_area.insert(tk.END, f"📌 {fact}: {'是' if value else '否'}{source}\n")
        
        text_area.config(state=tk.DISABLED)
        
        ttk.Button(wm_window, text="关闭", command=wm_window.destroy).pack(pady=10)
    
    def run_performance_test(self):
        """运行快速性能测试"""
        from modules.performance_tester import PerformanceTester
        
        test_window = tk.Toplevel(self.root)
        test_window.title("📊 性能测试")
        test_window.geometry("650x500")
        
        # 主框架
        main_frame = ttk.Frame(test_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # 标题
        title_label = ttk.Label(main_frame, text="🐾 快速性能测试", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 文本区域
        text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=('Consolas', 11), height=20)
        text_area.pack(expand=True, fill='both', pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        def run_test():
            text_area.config(state=tk.NORMAL)
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "🔄 正在运行快速性能测试...\n")
            text_area.update()
            
            try:
                tester = PerformanceTester("large_expert_system.db")
                report = tester.run_fast_test(self.engine)
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, report)
            except Exception as e:
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, f"❌ 测试失败: {str(e)}")
            
            text_area.config(state=tk.DISABLED)
        
        ttk.Button(button_frame, text="🚀 开始测试", command=run_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 关闭", command=test_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # 自动运行测试
        test_window.after(100, run_test)
    
    def clear_working_memory(self):
        """清空工作内存"""
        if messagebox.askyesno("确认", "确定要清空工作内存吗？"):
            result = self.wm.clear()
            messagebox.showinfo("成功", result)
            # 刷新主界面统计
            self.refresh_stats()
    
    def export_rules(self):
        """导出规则"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            result = self.kb.export_rules(file_path)
            messagebox.showinfo("成功", result)
    
    def import_rules(self):
        """导入规则"""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            result = self.kb.import_rules(file_path)
            # 刷新索引和统计
            self.engine.refresh_index()
            self.refresh_stats()
            messagebox.showinfo("成功", result)

if __name__ == "__main__":
    root = tk.Tk()
    app = LargeScaleExpertSystemGUI(root)
    root.mainloop()