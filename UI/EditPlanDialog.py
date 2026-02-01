from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class EditPlanDialog(QDialog):
    def __init__(self, child_id, db):
        super().__init__()
        self.child_id = child_id
        self.db = db
        self.setWindowTitle("编辑学习计划")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        self.rows = []
        self.rows_layout = QVBoxLayout()
        for name, pts in self.db.get_plan(child_id):
            self.add_row(name, pts)
        add_btn = QPushButton("添加任务")
        add_btn.clicked.connect(lambda: self.add_row("", 5))
        btns = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(self.rows_layout)
        layout.addWidget(add_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

    def add_row(self, name, pts):
        h = QHBoxLayout()
        le = QLineEdit(name)
        sb = QSpinBox()
        sb.setRange(1,100)
        sb.setValue(pts)
        rem = QPushButton("删除")
        rem.clicked.connect(lambda: self.remove_row(h))
        h.addWidget(le)
        h.addWidget(sb)
        h.addWidget(rem)
        self.rows_layout.addLayout(h)
        self.rows.append((h, le, sb))

    def remove_row(self, layout):
        for i,(h,le,sb) in enumerate(self.rows):
            if h is layout:
                while h.count():
                    w = h.takeAt(0).widget()
                    if w:
                        w.deleteLater()
                self.rows_layout.removeItem(h)
                self.rows.pop(i)
                break

    def save(self):
        tasks = []
        for h, le, sb in self.rows:
            name = le.text().strip()
            if name:
                tasks.append((name, sb.value()))
        self.db.update_plan(self.child_id, tasks)
        self.accept()