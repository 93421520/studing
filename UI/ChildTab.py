from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ChildTab(QWidget):
    """单个小朋友的打卡标签页"""
    def __init__(self, child_id, name, db, logic, restricted=False):
        super().__init__()
        self.child_id = child_id
        self.name = name
        self.db = db
        self.logic = logic
        self.restricted = restricted
        
        layout = QVBoxLayout()
        title_font = QFont()
        title_font.setPointSize(12)
        self.label_title = QLabel(f"{name}")
        self.label_title.setFont(title_font)
        layout.addWidget(self.label_title)

        self.label_points = QLabel(f"积分: {self.db.get_points(child_id)}")
        layout.addWidget(self.label_points)

        last = self.db.get_last_record_date(child_id)
        last_str = last if last else "未打卡"
        self.label_last = QLabel(f"最近打卡: {last_str}")
        layout.addWidget(self.label_last)
        
        self.task_widgets = []
        plan = self.db.get_plan(child_id)
        for task_name, pts in plan:
            cb = QCheckBox(f"{task_name} ({pts}分)")
            layout.addWidget(cb)
            self.task_widgets.append((task_name, cb))
            
        btns = QHBoxLayout()
        self.btn_submit = QPushButton("今日打卡签字")
        self.btn_submit.clicked.connect(self.submit)
        btns.addWidget(self.btn_submit)
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.clicked.connect(self.refresh)
        btns.addWidget(self.btn_refresh)

        if not self.restricted:
            self.btn_edit = QPushButton("编辑学习计划")
            self.btn_edit.clicked.connect(self.open_edit_dialog)
            btns.addWidget(self.btn_edit)

        layout.addLayout(btns)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.label_points.setText(f"积分: {self.db.get_points(self.child_id)}")
        last = self.db.get_last_record_date(self.child_id)
        self.label_last.setText(f"最近打卡: {last if last else '未打卡'}")
        # 禁用今日已打卡
        from datetime import date
        today = date.today().isoformat()
        if self.db.has_record_for_date(self.child_id, today):
            self.btn_submit.setEnabled(False)
            for name, cb in self.task_widgets:
                cb.setEnabled(False)
        else:
            self.btn_submit.setEnabled(True)
            for name, cb in self.task_widgets:
                cb.setEnabled(True)

    def submit(self):
        done = [name for name, cb in self.task_widgets if cb.isChecked()]
        total, ok, msg = self.logic.submit_daily(self.child_id, done)
        if not ok and msg == "already_submitted":
            QMessageBox.warning(self, "提示", "您今天已经打卡过了！")
            self.refresh()
            return
        QMessageBox.information(self, "完成", f"打卡成功，获得 {total} 积分！")
        self.refresh()

    def open_edit_dialog(self):
        from UI.EditPlanDialog import EditPlanDialog
        dlg = EditPlanDialog(self.child_id, self.db)
        if dlg.exec_():
            self.refresh()