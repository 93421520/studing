from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from datetime import date, timedelta

class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout()
        form = QFormLayout()
        self.combo = QComboBox()
        self.combo.addItem("所有孩子", None)
        self.mapping = {None: None}
        for cid, name in db.get_children():
            self.combo.addItem(name, cid)
            self.mapping[name] = cid
        self.start = QDateEdit()
        self.start.setDate(date.today() - timedelta(days=30))
        self.end = QDateEdit()
        self.end.setDate(date.today())
        form.addRow("孩子", self.combo)
        form.addRow("开始", self.start)
        form.addRow("结束", self.end)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_run = QPushButton("生成报表")
        btn_run.clicked.connect(self.run_report)
        btns.addWidget(btn_run)
        btn_export = QPushButton("导出 CSV")
        btn_export.clicked.connect(self.export_csv)
        btns.addWidget(btn_export)
        layout.addLayout(btns)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["日期", "任务", "积分"])
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        # 重新填充孩子列表
        self.combo.clear()
        self.combo.addItem("所有孩子", None)
        for cid, name in self.db.get_children():
            self.combo.addItem(name, cid)

    def run_report(self):
        cid = self.combo.currentData()
        s = self.start.date().toString('yyyy-MM-dd')
        e = self.end.date().toString('yyyy-MM-dd')
        records = self.db.get_records(child_id=cid, start_date=s, end_date=e)
        self.table.setRowCount(0)
        for d, tasks, pts in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(d))
            self.table.setItem(row, 1, QTableWidgetItem(', '.join(tasks)))
            self.table.setItem(row, 2, QTableWidgetItem(str(pts)))

    def export_csv(self):
        cid = self.combo.currentData()
        s = self.start.date().toString('yyyy-MM-dd')
        e = self.end.date().toString('yyyy-MM-dd')
        records = self.db.get_records(child_id=cid, start_date=s, end_date=e)
        path, _ = QFileDialog.getSaveFileName(self, "导出 CSV", "report.csv", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('date,tasks,points\n')
                for d, tasks, pts in records:
                    f.write(f"{d},\"{';'.join(tasks)}\",{pts}\n")
            QMessageBox.information(self, "导出", "已导出 CSV")