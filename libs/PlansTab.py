from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from datetime import datetime

class PlansTab(QWidget):
    """家长端的任务管理与发布面板"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. 发布新任务区域
        form_group = QGroupBox("发布新任务")
        form_layout = QHBoxLayout()
        
        self.child_selector = QComboBox()
        self.db.cursor.execute("SELECT id, name FROM users WHERE role='child'")
        for cid, name in self.db.cursor.fetchall():
            self.child_selector.addItem(name, cid)
        self.child_selector.currentIndexChanged.connect(self.load_current_tasks)
            
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("请输入任务内容...")
        
        self.pts_input = QSpinBox()
        self.pts_input.setRange(5, 100)
        self.pts_input.setValue(20)
        
        btn_add = QPushButton("确认发布")
        btn_add.clicked.connect(self.add_task)
        
        form_layout.addWidget(QLabel("执行孩子:"))
        form_layout.addWidget(self.child_selector)
        form_layout.addWidget(QLabel("内容:"))
        form_layout.addWidget(self.task_input)
        form_layout.addWidget(QLabel("积分:"))
        form_layout.addWidget(self.pts_input)
        form_layout.addWidget(btn_add)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # 2. 今日任务列表（可编辑）
        layout.addWidget(QLabel("📅 今日已发布任务 (双击内容可直接编辑):"))
        self.task_table = QTableWidget(0, 4)
        self.task_table.setHorizontalHeaderLabels(["任务名称", "分值", "当前状态", "操作"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.task_table.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.task_table)

        self.load_current_tasks()

    def load_current_tasks(self):
        """加载选定孩子今天的任务列表"""
        self.task_table.blockSignals(True)
        self.task_table.setRowCount(0)
        child_id = self.child_selector.currentData()
        if not child_id: return
        
        tasks = self.db.get_today_tasks(child_id)
        for i, (tid, name, pts, status) in enumerate(tasks):
            self.task_table.insertRow(i)
            
            # 任务名称
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, tid)
            self.task_table.setItem(i, 0, name_item)
            
            # 分值
            self.task_table.setItem(i, 1, QTableWidgetItem(str(pts)))
            
            # 状态 (不可编辑)
            st_txt = "已获签" if status == 2 else "待签字" if status == 1 else "进行中"
            st_item = QTableWidgetItem(st_txt)
            st_item.setFlags(st_item.flags() & ~Qt.ItemIsEditable)
            self.task_table.setItem(i, 2, st_item)
            
            # 删除按钮
            del_btn = QPushButton("删除")
            del_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            del_btn.clicked.connect(lambda _, t=tid: self.delete_task(t))
            self.task_table.setCellWidget(i, 3, del_btn)
            
        self.task_table.blockSignals(False)

    def add_task(self):
        name = self.task_input.text().strip()
        if not name: return
        cid = self.child_selector.currentData()
        self.db.add_task(cid, name, self.pts_input.value())
        self.task_input.clear()
        self.load_current_tasks()

    def on_item_changed(self, item):
        """处理单元格编辑后的保存逻辑"""
        row = item.row()
        tid = self.task_table.item(row, 0).data(Qt.UserRole)
        name = self.task_table.item(row, 0).text()
        try:
            pts = int(self.task_table.item(row, 1).text())
            self.db.update_task(tid, name, pts)
        except ValueError:
            QMessageBox.warning(self, "错误", "积分必须为数字！")
            self.load_current_tasks()

    def delete_task(self, tid):
        if QMessageBox.question(self, "确认", "确定要删除这个任务吗？") == QMessageBox.Yes:
            self.db.delete_task(tid)
            self.load_current_tasks()