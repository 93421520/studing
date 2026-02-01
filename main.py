import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libs.Database import Database
from works.StudyLogic import StudyLogic
from UI.TrainCanvas import TrainCanvas

class TrainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.logic = StudyLogic(self.db)
        self.current_child_id = 1
        self.current_role = "child"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("蒸汽火车进阶学习系统 v3.5")
        self.resize(1100, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        
        # 顶部：身份切换栏
        top_bar = QHBoxLayout()
        self.info_lbl = QLabel("👦 当前视图：大宝")
        self.info_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        btn_switch = QPushButton("🔄 切换登录角色")
        btn_switch.clicked.connect(self.switch_role)
        top_bar.addWidget(self.info_lbl)
        top_bar.addStretch()
        top_bar.addWidget(btn_switch)
        self.main_layout.addLayout(top_bar)

        # 核心内容：堆叠窗口
        self.stack = QStackedWidget()
        self.init_child_ui()
        self.init_parent_ui()
        self.main_layout.addWidget(self.stack)

        self.refresh_all()

    def init_child_ui(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        self.canvas = TrainCanvas()
        lay.addWidget(self.canvas)
        self.points_lbl = QLabel("💰 当前积分：0")
        self.points_lbl.setStyleSheet("font-size: 22px; color: #d35400; margin: 10px 0;")
        lay.addWidget(self.points_lbl)
        self.task_table = QTableWidget(0, 3)
        self.task_table.setHorizontalHeaderLabels(["学习任务", "预设积分", "当前状态"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.task_table)
        btn_submit = QPushButton("🚀 完成选定任务 (送交家长签字)")
        btn_submit.setFixedHeight(50)
        btn_submit.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_submit.clicked.connect(self.submit_current_task)
        lay.addWidget(btn_submit)
        self.stack.addWidget(page)

    def init_parent_ui(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        tabs = QTabWidget()
        p1 = QWidget()
        p1_lay = QVBoxLayout(p1)
        self.approve_table = QTableWidget(0, 4)
        self.approve_table.setHorizontalHeaderLabels(["孩子", "任务内容", "提交日期", "质量评价 & 签字"])
        self.approve_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        p1_lay.addWidget(self.approve_table)
        tabs.addTab(p1, "待办签字箱")
        p2 = QWidget()
        p2_lay = QFormLayout(p2)
        self.in_target = QComboBox()
        self.in_target.addItems(["大宝", "小宝"])
        self.in_name = QLineEdit()
        self.in_pts = QSpinBox()
        self.in_pts.setRange(5, 200)
        self.in_pts.setValue(20)
        btn_add = QPushButton("确认发布预设任务")
        btn_add.clicked.connect(self.add_new_task)
        p2_lay.addRow("执行对象:", self.in_target)
        p2_lay.addRow("任务描述:", self.in_name)
        p2_lay.addRow("基础分值:", self.in_pts)
        p2_lay.addRow(btn_add)
        tabs.addTab(p2, "发布新任务")
        lay.addWidget(tabs)
        self.stack.addWidget(page)

    def switch_role(self):
        menu = QMenu(self)
        a1 = menu.addAction("👧 大宝")
        a2 = menu.addAction("👶 小宝")
        a3 = menu.addAction("👔 家长管理后台")
        res = menu.exec_(QCursor.pos())
        if res == a1: self.current_child_id, self.current_role = 1, "child"
        elif res == a2: self.current_child_id, self.current_role = 2, "child"
        elif res == a3: self.current_role = "parent"
        else: return
        self.info_lbl.setText(f"当前视图：{res.text()}")
        self.stack.setCurrentIndex(0 if self.current_role == "child" else 1)
        self.refresh_all()

    def refresh_all(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.current_role == "child":
            tasks = self.db.get_tasks_by_date(self.current_child_id, today)
            cars = [(t[4], t[1]) for t in tasks if t[3] == 2]
            self.canvas.set_data(cars)
            self.task_table.setRowCount(len(tasks))
            for i, t in enumerate(tasks):
                self.task_table.setItem(i, 0, QTableWidgetItem(t[1]))
                self.task_table.setItem(i, 1, QTableWidgetItem(str(t[2])))
                status_txt = "🌟 已获得车厢" if t[3]==2 else "⏳ 审核中" if t[3]==1 else "📅 今日待办"
                self.task_table.setItem(i, 2, QTableWidgetItem(status_txt))
                self.task_table.item(i, 0).setData(Qt.UserRole, t[0])
            p_res = self.db.cursor.execute("SELECT points FROM wallet WHERE child_id=?", (self.current_child_id,)).fetchone()
            self.points_lbl.setText(f"💰 累计总积分：{p_res[0] if p_res else 0}")
        else:
            self.db.cursor.execute("""SELECT tasks.id, users.name, tasks.name, tasks.date FROM tasks JOIN users ON tasks.child_id = users.id WHERE tasks.status = 1""")
            rows = self.db.cursor.fetchall()
            self.approve_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.approve_table.setItem(i, 0, QTableWidgetItem(r[1]))
                self.approve_table.setItem(i, 1, QTableWidgetItem(r[2]))
                self.approve_table.setItem(i, 2, QTableWidgetItem(r[3]))
                btns = QWidget()
                bl = QHBoxLayout(btns); bl.setContentsMargins(0,0,0,0)
                for lbl, key, color in [("豪华", "luxury", "#f1c40f"), ("标准", "standard", "#3498db"), ("基础", "basic", "#95a5a6")]:
                    b = QPushButton(lbl); b.setStyleSheet(f"background-color: {color}; color: white;")
                    b.clicked.connect(lambda ch, tid=r[0], ql=key: self.approve_callback(tid, ql))
                    bl.addWidget(b)
                self.approve_table.setCellWidget(i, 3, btns)

    def submit_current_task(self):
        row = self.task_table.currentRow()
        if row < 0: return
        tid = self.task_table.item(row, 0).data(Qt.UserRole)
        self.logic.submit_task(tid)
        self.refresh_all()

    def approve_callback(self, tid, quality):
        pts = self.logic.approve_task(tid, quality)
        self.refresh_all()

    def add_new_task(self):
        name = self.in_name.text()
        if not name: return
        cid = 1 if self.in_target.currentText() == "大宝" else 2
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.add_task(cid, today, name, self.in_pts.value())
        self.in_name.clear()
        self.refresh_all()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TrainApp()
    win.show()
    sys.exit(app.exec_())