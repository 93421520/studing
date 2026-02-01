import sqlite3
import json
from datetime import date

class Database:
    def __init__(self, db_path="study_train.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_schema()

    def _init_schema(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tasks 
            (id INTEGER PRIMARY KEY, child_id INTEGER, date TEXT, name TEXT, points INTEGER, status INTEGER, quality TEXT)""")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS wallet (child_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0)")
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO users (name, role) VALUES ('大宝', 'child'), ('小宝', 'child'), ('家长', 'parent')")
            self.cursor.execute("INSERT INTO wallet (child_id, points) VALUES (1, 0), (2, 0)")
        self.conn.commit()

    def get_tasks_by_date(self, child_id, date):
        return self.cursor.execute("SELECT id, name, points, status, quality FROM tasks WHERE child_id=? AND date= ?", (child_id, date)).fetchall()

    def add_task(self, child_id, date, name, pts):
        self.cursor.execute("INSERT INTO tasks (child_id, date, name, points, status, quality) VALUES (?,?,?,?,0,'basic')", (child_id, date, name, pts))
        self.conn.commit()


class DBManager:
    def __init__(self, db_name="study_system.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. 小朋友信息表，增加 password 字段
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS children 
                            (id INTEGER PRIMARY KEY, name TEXT UNIQUE, password TEXT)''')
        # 2. 学习计划表 (每个孩子有不同的任务)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS plans 
                            (id INTEGER PRIMARY KEY, child_id INTEGER, task_name TEXT, 
                             points_per_task INTEGER, FOREIGN KEY(child_id) REFERENCES children(id))''')
        # 3. 积分钱包
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wallet 
                            (child_id INTEGER PRIMARY KEY, points INTEGER, 
                             FOREIGN KEY(child_id) REFERENCES children(id))''')
        # 4. 打卡记录表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS records
                            (id INTEGER PRIMARY KEY, child_id INTEGER, date TEXT, tasks TEXT, points INTEGER,
                             FOREIGN KEY(child_id) REFERENCES children(id))''')
        self.conn.commit()
        # 兼容老数据库，尝试添加 password 列（若已存在会抛错）
        try:
            self.cursor.execute("ALTER TABLE children ADD COLUMN password TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def add_child(self, name, password=None):
        # 默认密码为 123456（如果未指定）
        if password is None:
            password = '123456'
        try:
            self.cursor.execute("INSERT INTO children (name, password) VALUES (?, ?)", (name, password))
            cid = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO wallet VALUES (?, 0)", (cid,))
            self.conn.commit()
            return cid
        except sqlite3.IntegrityError:
            return None

    def delete_child(self, child_id):
        # 删除与孩子相关的所有数据
        self.cursor.execute("DELETE FROM records WHERE child_id=?", (child_id,))
        self.cursor.execute("DELETE FROM plans WHERE child_id=?", (child_id,))
        self.cursor.execute("DELETE FROM wallet WHERE child_id=?", (child_id,))
        self.cursor.execute("DELETE FROM children WHERE id=?", (child_id,))
        self.conn.commit()

    def get_children(self):
        return self.cursor.execute("SELECT id, name FROM children").fetchall()

    def get_plan(self, child_id):
        return self.cursor.execute("SELECT task_name, points_per_task FROM plans WHERE child_id=?", (child_id,)).fetchall()

    def update_plan(self, child_id, tasks):
        self.cursor.execute("DELETE FROM plans WHERE child_id=?", (child_id,))
        for name, pts in tasks:
            self.cursor.execute("INSERT INTO plans (child_id, task_name, points_per_task) VALUES (?, ?, ?)", 
                                (child_id, name, pts))
        self.conn.commit()

    def get_points(self, child_id):
        row = self.cursor.execute("SELECT points FROM wallet WHERE child_id=?", (child_id,)).fetchone()
        return row[0] if row else 0

    def update_points(self, child_id, added):
        current = self.get_points(child_id)
        self.cursor.execute("UPDATE wallet SET points=? WHERE child_id=?", (current + added, child_id))
        self.conn.commit()

    def add_record(self, child_id, date_str, tasks, points):
        tasks_json = json.dumps(tasks, ensure_ascii=False)
        self.cursor.execute("INSERT INTO records (child_id, date, tasks, points) VALUES (?, ?, ?, ?)",
                            (child_id, date_str, tasks_json, points))
        self.conn.commit()

    def has_record_for_date(self, child_id, date_str):
        row = self.cursor.execute("SELECT COUNT(1) FROM records WHERE child_id=? AND date=?", (child_id, date_str)).fetchone()
        return row[0] > 0

    def get_last_record_date(self, child_id):
        row = self.cursor.execute("SELECT date FROM records WHERE child_id=? ORDER BY date DESC LIMIT 1", (child_id,)).fetchone()
        return row[0] if row else None

    def get_records(self, child_id=None, start_date=None, end_date=None):
        """返回 (date, tasks_list, points) 的列表，按日期降序"""
        query = "SELECT date, tasks, points FROM records"
        params = []
        clauses = []
        if child_id is not None:
            clauses.append("child_id=?")
            params.append(child_id)
        if start_date is not None:
            clauses.append("date>=?")
            params.append(start_date)
        if end_date is not None:
            clauses.append("date<=?")
            params.append(end_date)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY date DESC"
        rows = self.cursor.execute(query, params).fetchall()
        return [(r[0], json.loads(r[1]), r[2]) for r in rows]

    def set_password(self, child_id, password):
        self.cursor.execute("UPDATE children SET password=? WHERE id=?", (password, child_id))
        self.conn.commit()

    def check_password(self, child_id, password):
        row = self.cursor.execute("SELECT password FROM children WHERE id=?", (child_id,)).fetchone()
        if row and row[0]:
            return row[0] == password
        return False