from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from datetime import date

class QuickCheckDialog(QDialog):
    def __init__(self, db, logic):
        super().__init__()
        self.db = db
        self.logic = logic
        self.setWindowTitle("快速打卡")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        self.combo = QComboBox()
        for cid, name in db.get_children():
            self.combo.addItem(name, cid)
        self.combo.currentIndexChanged.connect(self.load_tasks)
        layout.addWidget(self.combo)
        self.tasks_layout = QVBoxLayout()
        layout.addLayout(self.tasks_layout)
        btns = QHBoxLayout()
        ok = QPushButton("提交")
        ok.clicked.connect(self.submit)
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.load_tasks()

    def load_tasks(self):
        # 清空
        while self.tasks_layout.count():
            w = self.tasks_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        cid = self.combo.currentData()
        if cid is None:
            return
        for name, pts in self.db.get_plan(cid):
            cb = QCheckBox(f"{name} ({pts}分)")
            self.tasks_layout.addWidget(cb)
        # store checkboxes
        self.checkboxes = [self.tasks_layout.itemAt(i).widget() for i in range(self.tasks_layout.count())]

    def submit(self):
        cid = self.combo.currentData()
        done = []
        for cb in self.checkboxes:
            if cb.isChecked():
                txt = cb.text()
                name = txt.split(' (')[0]
                done.append(name)
        total, ok, msg = self.logic.submit_daily(cid, done)
        if not ok:
            QMessageBox.warning(self, "失败", "今天已打卡或发生错误")
            self.reject()
            return
        QMessageBox.information(self, "完成", f"打卡成功，获得 {total} 积分！")
        self.accept()