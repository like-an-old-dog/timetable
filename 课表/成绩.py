import tkinter as tk
from tkinter import ttk, messagebox, font
import requests
import json
import re
import base64

# ==================== 常量定义 ====================
LOGIN_URL = 'https://jwxt.gdupt.edu.cn/login!doLogin.action'
COURSE_URL = 'https://jwxt.gdupt.edu.cn/xsgrkbcx!xsAllKbList.action'
LOGIN2 = 'https://jwxt.gdupt.edu.cn/login'
SCORE_URL = 'https://jwxt.gdupt.edu.cn/xskccjxx!getDataList.action'

# 固定的学号和密码
FIXED_USERNAME = '24034530116'
FIXED_PASSWORD = 'LiYuhan060317@@'

headers = {
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
    'Referer': LOGIN2
}

session = requests.Session()

# ==================== 核心功能 ====================

def login():
    """使用固定的学号和密码登录"""
    try:
        session.get(LOGIN2, headers=headers)
        encoded_pwd = base64.b64encode(FIXED_PASSWORD.encode()).decode()

        login_data = {
            'account': FIXED_USERNAME,
            'pwd': encoded_pwd,
            'verifycode': ''
        }

        response = session.post(LOGIN_URL, data=login_data, headers=headers)
        if "不正确" in response.text:
            messagebox.showerror("登录失败", "账号或密码错误")
            return False
        return True
    except Exception as e:
        messagebox.showerror("网络错误", f"登录失败: {str(e)}")
        return False

def get_score_data(semester):
    """获取成绩数据"""
    try:
        score_data = {
            'xnxqdm': semester,
            'jhlxdm': '',
            'page': 1,
            'rows': 20,
            'sort': 'xnxqdm,kcbh,ksxzdm',
            'order': 'asc'
        }

        response = session.post(
            SCORE_URL,
            data=score_data,
            headers=headers
        )
        
        # 解析JSON响应
        score_json = json.loads(response.text)
        return score_json
    except Exception as e:
        messagebox.showerror("网络错误", f"数据获取失败: {str(e)}")
        return None

def calculate_gpa(score):
    """根据分数计算绩点"""
    try:
        score = float(score)
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 80:
            return 3.3
        elif score >= 75:
            return 3.0
        elif score >= 70:
            return 2.7
        elif score >= 65:
            return 2.3
        elif score >= 60:
            return 2.0
        else:
            return 0.0
    except:
        return 0.0

# ==================== GUI界面 ====================
class ScoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("广油成绩查询系统")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        
        # 设置中文字体
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="SimHei", size=10)
        self.root.option_add("*Font", self.default_font)
        
        # 主题颜色
        self.colors = {
            "primary": "#4a7abc",
            "secondary": "#5cb85c",
            "accent": "#f0ad4e",
            "background": "#f8f9fa",
            "text": "#000000",
            "light_text": "#6c757d",
            "border": "#dee2e6",
            "highlight": "#007bff",
            "danger": "#dc3545"
        }
        
        # 设置界面样式
        self.setup_styles()
        
        # 变量初始化
        self.semester = tk.StringVar(value="202402")
        self.year_var = tk.StringVar(value="2024")
        self.term_var = tk.StringVar(value="2")
        self.scores = []
        
        # 初始化UI
        self.setup_ui()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 创建自定义样式
        style.configure(
            "Main.TFrame",
            background=self.colors["background"]
        )
        
        style.configure(
            "Header.TLabel",
            font=font.Font(family="Microsoft YaHei", size=14, weight="bold"),
            foreground="#333333",
            background=self.colors["background"]
        )
        
        style.configure(
            "Normal.TLabel",
            font=font.Font(family="Microsoft YaHei", size=12),
            foreground="#555555",
            background=self.colors["background"]
        )
        
        style.configure(
            "Primary.TButton",
            font=font.Font(family="Microsoft YaHei", size=11, weight="bold"),
            foreground="white",
            background="#4CAF50",
            padding=6
        )
        style.map("Primary.TButton",
                 background=[("active", "#45a049")],
                 foreground=[("active", "white")])
        
        style.configure(
            "Secondary.TButton",
            font=font.Font(family="Microsoft YaHei", size=11),
            foreground="white",
            background="#2196F3",
            padding=6
        )
        style.map("Secondary.TButton",
                 background=[("active", "#0b7dda")],
                 foreground=[("active", "white")])
        
        style.configure(
            "Accent.TButton",
            font=font.Font(family="Microsoft YaHei", size=11),
            foreground="white",
            background="#FF9800",
            padding=6
        )
        style.map("Accent.TButton",
                 background=[("active", "#e68a00")],
                 foreground=[("active", "white")])
        
        style.configure(
            "TEntry",
            font=font.Font(family="Microsoft YaHei", size=11),
            padding=6
        )
        
        style.configure(
            "Treeview",
            font=font.Font(family="Microsoft YaHei", size=11),
            background="white",
            foreground="#333333",
            rowheight=35,
            fieldbackground="white"
        )
        
        style.configure(
            "Treeview.Heading",
            font=font.Font(family="Microsoft YaHei", size=11, weight="bold"),
            background="#f5f5f5",
            foreground="#333333",
            padding=8
        )
        style.map("Treeview.Heading",
                 background=[("active", "#e0e0e0")],
                 foreground=[("active", "#333333")])
        
        # 为表格行添加交替颜色
        style.map("Treeview",
                 background=[("selected", "#2196F3"), ("!selected", "white")],
                 foreground=[("selected", "white"), ("!selected", "#333333")])
    
    def setup_ui(self):
        """初始化界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # 应用标题
        title_label = ttk.Label(
            main_frame, 
            text="广油成绩查询系统", 
            font=font.Font(family="Microsoft YaHei", size=22, weight="bold")
        )
        title_label.pack(pady=(0, 30))

        # 学期选择面板 - 现代化卡片式设计
        semester_frame = ttk.Frame(main_frame, style="Main.TFrame")
        semester_frame.pack(fill='x', pady=(0, 30))
        
        # 添加卡片效果
        semester_card = ttk.Frame(semester_frame, padding=20)
        semester_card.pack(fill='x')
        
        # 使用网格布局，居中对齐
        semester_card.grid_columnconfigure(0, weight=1)
        semester_card.grid_columnconfigure(5, weight=1)
        
        ttk.Label(semester_card, text="年份:", font=font.Font(family="Microsoft YaHei", size=12)).grid(row=0, column=1, sticky='e', padx=10, pady=10)
        
        # 年份下拉框
        years = [str(year) for year in range(2020, 2031)]  # 2020-2030年
        year_combo = ttk.Combobox(semester_card, textvariable=self.year_var, values=years, width=10, state="readonly")
        year_combo.grid(row=0, column=2, padx=10, pady=10)
        year_combo.current(years.index("2024")) 
        
        ttk.Label(semester_card, text="学期:", font=font.Font(family="Microsoft YaHei", size=12)).grid(row=0, column=3, sticky='e', padx=10, pady=10)
        
        # 学期下拉框
        terms = ["1", "2"]
        term_combo = ttk.Combobox(semester_card, textvariable=self.term_var, values=terms, width=8, state="readonly")
        term_combo.grid(row=0, column=4, padx=10, pady=10)
        term_combo.current(1)  
        
        # 查询按钮
        query_button = ttk.Button(semester_card, text="查询成绩", command=self.query_scores, style="Primary.TButton")
        query_button.grid(row=0, column=5, padx=20, pady=10, sticky='w')

        # 成绩表格 - 现代化设计
        self.score_frame = ttk.Frame(main_frame)
        self.score_frame.pack(fill='both', expand=True, pady=(0, 30))
        
        # 表格标题
        table_title = ttk.Label(
            self.score_frame, 
            text="成绩列表", 
            font=font.Font(family="Microsoft YaHei", size=14, weight="bold")
        )
        table_title.pack(anchor='w', pady=(0, 15))
        
        # 创建带有边框效果的表格容器
        table_container = ttk.Frame(self.score_frame, padding=10, relief="solid", borderwidth=1)
        table_container.pack(fill='both', expand=True)

        # 表格和滚动条
        self.tree = ttk.Treeview(table_container, show='headings')
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # 使用网格布局
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # 初始化表格列 - 更合理的列宽
        columns = ["序号", "课程名称", "课程类型", "学分", "成绩", "绩点"]
        self.tree["columns"] = columns
        column_widths = [80, 250, 120, 80, 80, 80]
        
        for i, col in enumerate(columns):
            self.tree.column(col, width=column_widths[i], anchor='center', stretch=False)
            self.tree.heading(col, text=col)

        # 绩点统计 - 现代化卡片式设计
        self.gpa_frame = ttk.Frame(main_frame)
        self.gpa_frame.pack(fill='x')
        
        # 添加卡片效果
        gpa_card = ttk.Frame(self.gpa_frame, padding=25, relief="solid", borderwidth=1)
        gpa_card.pack(fill='x')
        
        # 平均绩点显示
        self.gpa_label = ttk.Label(
            gpa_card, 
            text="平均绩点: --", 
            font=font.Font(family="Microsoft YaHei", size=16, weight="bold")
        )
        self.gpa_label.pack(anchor='center')

    def query_scores(self):
        """查询成绩"""
        # 生成学期代码
        year = self.year_var.get()
        term = self.term_var.get().zfill(2)
        semester = year + term
        
        # 登录
        if not login():
            return
        
        # 获取成绩数据
        score_data = get_score_data(semester)
        if not score_data:
            return
        
        # 解析成绩数据
        self.scores = score_data.get('rows', [])
        
        # 按绩点排序
        self.scores.sort(key=lambda x: float(x.get('cjjd', 0)) if x.get('cjjd', '') else 0, reverse=True)
        
        # 计算平均绩点
        total_credits = 0
        total_gpa = 0
        
        # 清空表格
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # 填充表格
        for i, score in enumerate(self.scores):
            course_name = score.get('kcmc', '')
            course_type = score.get('kcdlmc', '')
            credits = score.get('xf', '0')
            score_value = score.get('zcj', '')
            gpa_value = score.get('cjjd', '0')
            
            # 累加学分和绩点
            try:
                credits_float = float(credits)
                gpa_float = float(gpa_value)
                total_credits += credits_float
                total_gpa += gpa_float * credits_float
            except:
                pass
            
            # 插入表格行
            self.tree.insert('', 'end', values=[
                i + 1,
                course_name,
                course_type,
                credits,
                score_value,
                gpa_value
            ])
        
        # 计算并显示平均绩点
        if total_credits > 0:
            avg_gpa = total_gpa / total_credits
            self.gpa_label.config(text=f"平均绩点: {avg_gpa:.2f}")
        else:
            self.gpa_label.config(text="平均绩点: --")

# ==================== 启动应用 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreApp(root)
    root.mainloop()