from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class PlansTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout()
        self.combo = QComboBox()
        layout.addWidget(QLabel("选择孩子以查看/编辑计划"))
        layout.addWidget(self.combo)
        self.table = QTableWidget(0,2)
        self.table.setHorizontalHeaderLabels(["任务", "积分"])
        layout.addWidget(self.table)
        btns = QHBoxLayout()
        self.btn_edit = QPushButton("编辑计划")
        self.btn_edit.clicked.connect(self.open_edit)
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.clicked.connect(self.refresh)
        btns.addWidget(self.btn_edit); btns.addWidget(self.btn_refresh)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.combo.clear()
        for cid, name in self.db.get_children():
            self.combo.addItem(name, cid)
        self.load_selected()

    def load_selected(self):
        cid = self.combo.currentData()
        self.table.setRowCount(0)
        if cid is None:
            return
        for name, pts in self.db.get_plan(cid):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(pts)))

    def open_edit(self):
        cid = self.combo.currentData()
        if cid is None:
            QMessageBox.warning(self, "错误", "请选择一个孩子")
            return
        from UI.EditPlanDialog import EditPlanDialog
        dlg = EditPlanDialog(cid, self.db)
        if dlg.exec_():
            QMessageBox.information(self, "完成", "学习计划已保存")
            self.load_selected()