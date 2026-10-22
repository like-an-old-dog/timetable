import tkinter as tk
from tkinter import ttk, messagebox, font
import requests
from bs4 import BeautifulSoup
import json
import pymysql
from pymysql import Error
import base64
import re

# ==================== 数据库配置 ====================
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'course_system',
    'charset': 'utf8mb4'
}

# ==================== 常量定义 ====================
LOGIN_URL = 'https://jwxt.gdupt.edu.cn/login!doLogin.action'
COURSE_URL = 'https://jwxt.gdupt.edu.cn/xsgrkbcx!xsAllKbList.action'
LOGIN2 = 'https://jwxt.gdupt.edu.cn/login'

headers = {
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
    'Referer': LOGIN2
}


# ==================== 数据库操作 ====================
def create_connection():
    """创建数据库连接"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror("数据库错误", f"连接失败: {str(e)}")
        return None


def init_database():
    """初始化数据库表结构"""
    conn = create_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS courses")
            cursor.execute("DROP TABLE IF EXISTS users")

            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE courses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    semester VARCHAR(6) NOT NULL,
                    course_name VARCHAR(255),
                    course_code VARCHAR(50),
                    class_name TEXT,
                    weeks TEXT,
                    day_of_week VARCHAR(10),
                    time_slot TEXT,
                    location TEXT,
                    teacher TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_semester (semester)
                )
            """)
        conn.commit()
    except Error as e:
        messagebox.showerror("数据库错误", f"初始化失败: {str(e)}")
    finally:
        conn.close()


def get_all_saved_accounts():
    """获取所有已保存的账号列表"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username FROM users ORDER BY last_login DESC")
            accounts = [row[0] for row in cursor.fetchall()]
            return accounts
    except Error as e:
        messagebox.showerror("数据库错误", f"获取账号列表失败: {str(e)}")
        return []
    finally:
        conn.close()


def get_user_password(username):
    """获取指定用户的密码"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Error as e:
        messagebox.showerror("数据库错误", f"获取密码失败: {str(e)}")
        return None
    finally:
        conn.close()


def update_user_login_time(username):
    """更新用户最后登录时间"""
    conn = create_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %s", (username,))
            conn.commit()
    except Error as e:
        messagebox.showerror("数据库错误", f"更新登录时间失败: {str(e)}")
    finally:
        conn.close()


def get_course_update_time(username, semester):
    """获取指定用户和学期的课程最后更新时间"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT MAX(update_time) 
                FROM courses c 
                JOIN users u ON c.user_id = u.id 
                WHERE u.username = %s AND c.semester = %s
            """, (username, semester))
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
    except Error as e:
        messagebox.showerror("数据库错误", f"获取更新时间失败: {str(e)}")
        return None
    finally:
        conn.close()


# init_database()

# ==================== 核心功能 ====================
session = requests.Session()


def validate_semester(semester):
    """验证学期格式"""
    return re.match(r"^\d{4}(0[1-9]|1[0-2])$", semester) is not None


def parse_weeks(week_str):
    """解析周数字符串为周数列表"""
    weeks = []
    for part in week_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            weeks.extend(range(start, end + 1))
        else:
            weeks.append(int(part))
    return weeks


def extract_course_info(html_content):
    """从HTML提取课程信息"""
    soup = BeautifulSoup(html_content, 'html.parser')
    courses = []

    script_tag = soup.find('script', string=lambda x: x and 'var kbxx = ' in x)
    if not script_tag:
        return courses

    try:
        json_str = script_tag.string.split('var kbxx = ')[1].split(';')[0]
        course_data = json.loads(json_str)

        for course in course_data:
            course_info = {
                'name': course.get('kcmc', ''),
                'code': course.get('kcbh', ''),
                'class': course.get('jxbmc', ''),
                'weeks': parse_weeks(course.get('zcs', '')),
                'day': int(course.get('xq', 0)),
                'time': list(map(int, course.get('jcdm2', '').split(','))),
                'location': course.get('jxcdmcs', ''),
                'teacher': course.get('teaxms', '')
            }
            courses.append(course_info)
    except Exception as e:
        messagebox.showerror("数据解析错误", str(e))

    return courses


# ==================== GUI界面 ====================
class CourseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("广油课程查询系统")
        self.root.geometry("1200x800")
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
            "text": "#000000",  # 加深文字颜色以提高可读性
            "light_text": "#6c757d",
            "border": "#dee2e6",
            "highlight": "#007bff",
            "danger": "#dc3545"
        }
        
        # 设置界面样式
        self.setup_styles()
        
        # 变量初始化
        self.current_week = tk.IntVar(value=1)
        self.semester = tk.StringVar(value="202401")
        self.year_var = tk.StringVar(value="2024")
        self.term_var = tk.StringVar(value="1")
        self.selected_account = tk.StringVar()
        self.courses = []
        
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
            font=font.Font(family="SimHei", size=12, weight="bold"),
            foreground="black",  # 改为黑色字体
            background=self.colors["background"]
        )
        
        style.configure(
            "Normal.TLabel",
            font=font.Font(family="SimHei", size=11),
            foreground="black",  # 改为黑色字体并增大字号
            background=self.colors["background"]
        )
        
        style.configure(
            "Primary.TButton",
            font=font.Font(family="SimHei", size=10),
            foreground="black",  # 改为黑色字体
            background=self.colors["primary"]
        )
        style.map("Primary.TButton",
                 background=[("active", "#3a6ab0")],
                 foreground=[("active", "black")])  # 激活状态也保持黑色
        
        style.configure(
            "Secondary.TButton",
            font=font.Font(family="SimHei", size=10),
            foreground="black",  # 改为黑色字体
            background=self.colors["secondary"]
        )
        style.map("Secondary.TButton",
                 background=[("active", "#4cae4c")],
                 foreground=[("active", "black")])  # 激活状态也保持黑色
        
        style.configure(
            "Accent.TButton",
            font=font.Font(family="SimHei", size=10),
            foreground="black",  # 改为黑色字体
            background=self.colors["accent"]
        )
        style.map("Accent.TButton",
                 background=[("active", "#eea236")],
                 foreground=[("active", "black")])  # 激活状态也保持黑色
        
        style.configure(
            "TEntry",
            font=font.Font(family="SimHei", size=10),
            padding=5
        )
        
        style.configure(
            "Treeview",
            font=font.Font(family="SimHei", size=11, weight="normal"),  
            background="white",
            foreground=self.colors["text"],  
            rowheight=80,  
            fieldbackground="white"
        )
        
        style.configure(
            "Treeview.Heading",
            font=font.Font(family="SimHei", size=10, weight="bold"),
            background=self.colors["primary"],
            foreground="black",  # 改为黑色字体
            padding=5
        )
        style.map("Treeview.Heading",
                 background=[("active", "#3a6ab0")],
                 foreground=[("active", "black")])  
        
        # 为表格行添加交替颜色
        style.configure("Treeview.Row",
                      background="white")
        style.map("Treeview",
                 background=[("selected", self.colors["highlight"])],
                 foreground=[("selected", "white")])
    
    def setup_ui(self):
        """初始化界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 应用标题
        title_label = ttk.Label(
            main_frame, 
            text="广油课程查询系统", 
            style="Header.TLabel",
            font=font.Font(family="SimHei", size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # 登录面板 - 使用网格布局更美观
        login_frame = ttk.LabelFrame(main_frame, text="用户登录", padding=15, style="Main.TFrame")
        login_frame.pack(fill='x', pady=(0, 20))
        
        login_grid = ttk.Frame(login_frame, style="Main.TFrame")
        login_grid.pack(pady=5)
        
        ttk.Label(login_grid, text="学期选择:", style="Normal.TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # 年份下拉框
        years = [str(year) for year in range(2020, 2031)]  # 2020-2030年
        year_combo = ttk.Combobox(login_grid, textvariable=self.year_var, values=years, width=6, state="readonly")
        year_combo.grid(row=0, column=1, padx=0, pady=5, sticky='w')
        year_combo.current(years.index("2024")) 
        
        # 年标签
        ttk.Label(login_grid, text="年", style="Normal.TLabel").grid(row=0, column=2, sticky='w', padx=0, pady=5)
        
        # 学期下拉框
        terms = ["1", "2"]
        term_combo = ttk.Combobox(login_grid, textvariable=self.term_var, values=terms, width=5, state="readonly")
        term_combo.grid(row=0, column=3, padx=0, pady=5, sticky='w')
        term_combo.current(0)  
        
        # 学期标签
        ttk.Label(login_grid, text="学期", style="Normal.TLabel").grid(row=0, column=4, sticky='w', padx=0, pady=5, columnspan=1)

        # 账号选择下拉框
        ttk.Label(login_grid, text="选择账号:", style="Normal.TLabel").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        # 获取已保存的账号列表
        saved_accounts = get_all_saved_accounts()
        self.account_combo = ttk.Combobox(login_grid, textvariable=self.selected_account, 
                                        values=saved_accounts if saved_accounts else ["暂无保存的账号"], 
                                        width=15, state="readonly")
        self.account_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='w')
        self.account_combo.bind("<<ComboboxSelected>>", self.on_account_selected)
        
        # 如果没有任何保存的账号，设置默认值
        if not saved_accounts:
            self.account_combo.current(0)
            self.account_combo.config(state="disabled")
        
        # 更新账号密码输入框的位置
        ttk.Label(login_grid, text="账号:", style="Normal.TLabel").grid(row=1, column=3, sticky='w', padx=5, pady=5)
        self.entry_username = ttk.Entry(login_grid, width=20)
        self.entry_username.grid(row=1, column=4, padx=5, pady=5)

        ttk.Label(login_grid, text="密码:", style="Normal.TLabel").grid(row=1, column=5, sticky='w', padx=5, pady=5)
        self.entry_password = ttk.Entry(login_grid, show="*", width=20)
        self.entry_password.grid(row=1, column=6, padx=5, pady=5)

        ttk.Button(login_grid, text="登录", command=self.login, style="Primary.TButton").grid(row=1, column=7, padx=10, pady=5)

        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="课表控制", padding=15, style="Main.TFrame")
        control_frame.pack(fill='x', pady=(0, 20))
        
        control_grid = ttk.Frame(control_frame, style="Main.TFrame")
        control_grid.pack(pady=5)
        
        ttk.Label(control_grid, text="选择周数:", style="Normal.TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.week_spin = ttk.Spinbox(
            control_grid, 
            from_=1, 
            to=20, 
            width=5,
            textvariable=self.current_week,
            command=self.update_timetable_display
        )
        self.week_spin.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(control_grid, text="更新课表", command=self.update_timetable_from_web, style="Secondary.TButton").grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(control_grid, text="查看课表", command=self.load_timetable_from_db, style="Accent.TButton").grid(row=0, column=3, padx=5, pady=5)

        # 课表表格 - 添加边框和美化
        self.timetable_frame = ttk.LabelFrame(main_frame, text="课程表", padding=15, style="Main.TFrame")
        self.timetable_frame.pack(fill='both', expand=True)
        
        # 创建带有边框效果的表格容器
        table_container = ttk.Frame(self.timetable_frame, style="Main.TFrame")
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

        # 初始化表格列 - 调整列宽
        columns = ["节次", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.tree["columns"] = columns
        column_widths = [80, 180, 180, 180, 180, 180, 180, 180]  
        
        for i, col in enumerate(columns):
            self.tree.column(col, width=column_widths[i], anchor='center', stretch=False)
            self.tree.heading(col, text=col)

    def on_account_selected(self, event=None):
        """当选择账号时自动填充密码"""
        selected_username = self.selected_account.get()
        if selected_username and selected_username != "暂无保存的账号":
            password = get_user_password(selected_username)
            if password:
                self.entry_username.delete(0, tk.END)
                self.entry_username.insert(0, selected_username)
                self.entry_password.delete(0, tk.END)
                self.entry_password.insert(0, password)
    
    def refresh_account_list(self):
        """刷新账号列表"""
        saved_accounts = get_all_saved_accounts()
        if saved_accounts:
            self.account_combo.config(values=saved_accounts, state="readonly")
            self.account_combo.current(0)
        else:
            self.account_combo.config(values=["暂无保存的账号"], state="disabled")
            self.account_combo.current(0)
    
    def validate_input(self):
        """验证输入有效性"""
        # 根据选择的年份和学期生成学期代码
        year = self.year_var.get()
        term = self.term_var.get().zfill(2)  # 格式化为两位数字
        self.semester.set(year + term)
        
        if not validate_semester(self.semester.get()):
            messagebox.showwarning("输入错误", "学期格式不正确")
            return False
        if not self.entry_username.get() or not self.entry_password.get():
            messagebox.showwarning("输入错误", "请输入账号和密码")
            return False
        return True

    def login(self):
        """处理登录逻辑"""
        if not self.validate_input():
            return

        username = self.entry_username.get()
        password = self.entry_password.get()
        semester = self.semester.get()

        conn = create_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
                    user_data = cursor.fetchone()

                    if user_data:
                        user_id, db_password = user_data
                        if password == db_password:
                            # 更新用户最后登录时间
                            update_user_login_time(username)
                            
                            cursor.execute("""
                                SELECT * FROM courses 
                                WHERE user_id = %s AND semester = %s
                            """, (user_id, semester))
                            courses = cursor.fetchall()
                            if courses:
                                self.load_courses_from_db(courses)
                            self.update_timetable_display()
                            # print("已展示课表")
                            return
            except Error as e:
                messagebox.showerror("数据库错误", f"查询失败: {str(e)}")
            finally:
                conn.close()

        self.fetch_from_website(username, password, semester)

    def load_courses_from_db(self, db_courses):
        """从数据库加载课程数据"""
        self.courses = []
        for course in db_courses:
            self.courses.append({
                'name': course[3],
                'code': course[4],
                'class': course[5],
                'weeks': parse_weeks(course[6]),
                'day': course[7],
                'time': list(map(int, course[8].split(','))),
                'location': course[9],
                'teacher': course[10],
            })

        self.update_timetable_display()
        print("已从数据库加载课表")

    def fetch_from_website(self, username, password, semester):
        """从网站获取数据"""
        try:
            session.get(LOGIN2, headers=headers)
            encoded_pwd = base64.b64encode(password.encode()).decode()

            login_data = {
                'account': username,
                'pwd': encoded_pwd,
                'verifycode': ''
            }

            response = session.post(LOGIN_URL, data=login_data, headers=headers)
            # print(response.text)
            if "不正确" in response.text:
                messagebox.showerror("登录失败", "账号或密码错误")
                return

            course_response = session.post(
                COURSE_URL,
                data={'xnxqdm': semester},
                headers=headers
            )
            self.courses = extract_course_info(course_response.text)

            if not self.courses:
                messagebox.showinfo("提示", "未找到课程数据")
                return

            self.save_to_database(username, password, semester)
            self.update_timetable_display()

        except Exception as e:
            messagebox.showerror("网络错误", f"数据获取失败: {str(e)}")

    def save_to_database(self, username, password, semester):
        """保存数据到数据库"""
        conn = create_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                # 始终保存或更新用户信息
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE password=VALUES(password)
                """, (username, password))

                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_result = cursor.fetchone()
                if user_result:
                    user_id = user_result[0]
                else:
                    # 如果用户不存在，插入新用户
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                    user_id = cursor.lastrowid

                # 删除旧学期数据
                cursor.execute("""
                    DELETE FROM courses 
                    WHERE user_id = %s AND semester = %s
                """, (user_id, semester))

                # 插入新数据
                for course in self.courses:
                    cursor.execute("""
                        INSERT INTO courses (
                            user_id, semester, course_name, course_code, class_name, 
                            weeks, day_of_week, time_slot, location, teacher
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        user_id,
                        semester,
                        course['name'],
                        course['code'],
                        course['class'],
                        ','.join(map(str, course['weeks'])),
                        course['day'],
                        ','.join(map(str, course['time'])),
                        course['location'],
                        course['teacher']
                    ))
                conn.commit()
                messagebox.showinfo("成功", f"{semester}学期数据已保存")
                # 刷新账号列表
                self.refresh_account_list()
        except Error as e:
            conn.rollback()
            messagebox.showerror("数据库错误", f"保存失败: {str(e)}")
        finally:
            conn.close()

    def refresh_data(self):
        """强制重新获取数据"""
        if self.validate_input():
            self.fetch_from_website(
                self.entry_username.get(),
                self.entry_password.get(),
                self.semester.get()
            )

    def update_timetable_from_web(self):
        """从网站更新课表数据"""
        if not self.entry_username.get() or not self.entry_password.get():
            messagebox.showwarning("提示", "请先登录")
            return
            
        # 先更新学期选择
        year = self.year_var.get()
        term = self.term_var.get().zfill(2)
        self.semester.set(year + term)
        
        username = self.entry_username.get()
        password = self.entry_password.get()
        semester = self.semester.get()
        
        try:
            session.get(LOGIN2, headers=headers)
            encoded_pwd = base64.b64encode(password.encode()).decode()

            login_data = {
                'account': username,
                'pwd': encoded_pwd,
                'verifycode': ''
            }

            response = session.post(LOGIN_URL, data=login_data, headers=headers)
            if "不正确" in response.text:
                messagebox.showerror("登录失败", "账号或密码错误")
                return

            course_response = session.post(
                COURSE_URL,
                data={'xnxqdm': semester},
                headers=headers
            )
            self.courses = extract_course_info(course_response.text)

            if not self.courses:
                messagebox.showinfo("提示", "未找到课程数据")
                return

            self.save_to_database(username, password, semester)
            self.update_timetable_display()
            
            # 显示更新时间
            update_time = get_course_update_time(username, semester)
            if update_time:
                messagebox.showinfo("成功", f"课表已更新！\n最后更新时间：{update_time}")
            else:
                messagebox.showinfo("成功", "课表已更新！")

        except Exception as e:
            messagebox.showerror("网络错误", f"数据获取失败: {str(e)}")

    def load_timetable_from_db(self):
        """从数据库加载课表数据"""
        if not self.entry_username.get():
            messagebox.showwarning("提示", "请先登录")
            return
            
        # 先更新学期选择
        year = self.year_var.get()
        term = self.term_var.get().zfill(2)
        self.semester.set(year + term)
        
        username = self.entry_username.get()
        semester = self.semester.get()
        
        conn = create_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, u.username 
                    FROM courses c 
                    JOIN users u ON c.user_id = u.id 
                    WHERE u.username = %s AND c.semester = %s
                    ORDER BY c.day_of_week, c.time_slot
                """, (username, semester))
                courses = cursor.fetchall()
                
                if not courses:
                    messagebox.showinfo("提示", "数据库中没有找到该学期的课程数据")
                    return
                    
                self.load_courses_from_db(courses)
                self.update_timetable_display()
                
                # 显示最后更新时间
                update_time = get_course_update_time(username, semester)
                if update_time:
                    messagebox.showinfo("成功", f"已从数据库加载课表！\n最后更新时间：{update_time}")
                else:
                    messagebox.showinfo("成功", "已从数据库加载课表！")
                    
        except Error as e:
            messagebox.showerror("数据库错误", f"加载失败: {str(e)}")
        finally:
            conn.close()

    def update_timetable_display(self):
        """更新课程表显示"""
        if not self.courses:
            messagebox.showinfo("提示", "当前无课程数据")
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        time_slots = {}
        selected_week = self.current_week.get()

        for course in self.courses:
            if selected_week not in course['weeks']:
                continue

            for time_slot in course['time']:
                key = (time_slot, course['day'])
                if key not in time_slots:
                    time_slots[key] = []
                time_slots[key].append(course)

        for time_slot in range(1, 13):
            row = [f"第{time_slot}节"] + [''] * 7
            for day in range(1, 8):
                courses = time_slots.get((time_slot, str(day)), [])
                if courses:
                    course = courses[0]
                    text = f"{course['name']}\n{course['location']}\n{course['teacher']}"
                    row[day] = text
            self.tree.insert('', 'end', values=row)


# ==================== 启动应用 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = CourseApp(root)
    root.mainloop()