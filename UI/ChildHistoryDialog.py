from PyQt5.QtWidgets import *
from datetime import date, timedelta

class ChildHistoryDialog(QDialog):
    def __init__(self, db, child_id):
        super().__init__()
        self.db = db
        self.child_id = child_id
        name = db.cursor.execute("SELECT name FROM children WHERE id=?", (child_id,)).fetchone()[0]
        self.setWindowTitle(f"{name} - 历史记录")
        self.resize(600, 400)
        layout = QVBoxLayout()
        form = QFormLayout()
        self.start = QDateEdit()
        self.start.setDate(date.today() - timedelta(days=30))
        self.end = QDateEdit()
        self.end.setDate(date.today())
        form.addRow("开始", self.start)
        form.addRow("结束", self.end)
        layout.addLayout(form)
        btns = QHBoxLayout()
        run = QPushButton("刷新")
        run.clicked.connect(self.run)
        btns.addWidget(run)
        export = QPushButton("导出 CSV")
        export.clicked.connect(self.export_csv)
        btns.addWidget(export)
        close = QPushButton("关闭")
        close.clicked.connect(self.accept)
        btns.addWidget(close)
        layout.addLayout(btns)

        self.table = QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels(["日期","任务","积分"]) 
        layout.addWidget(self.table)
        self.lbl_summary = QLabel("")
        layout.addWidget(self.lbl_summary)
        self.setLayout(layout)
        self.run()

    def run(self):
        s = self.start.date().toString('yyyy-MM-dd')
        e = self.end.date().toString('yyyy-MM-dd')
        records = self.db.get_records(child_id=self.child_id, start_date=s, end_date=e)
        self.table.setRowCount(0)
        total_pts = 0
        days = 0
        # count days in range
        ds = self.start.date().toPyDate()
        de = self.end.date().toPyDate()
        days = (de - ds).days + 1
        for d, tasks, pts in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(d))
            self.table.setItem(row, 1, QTableWidgetItem(', '.join(tasks)))
            self.table.setItem(row, 2, QTableWidgetItem(str(pts)))
            total_pts += pts
        avg = total_pts / days if days>0 else 0
        # 打卡率 = 有记录天数 / days
        recorded_days = len(set(r[0] for r in records))
        rate = recorded_days / days * 100 if days>0 else 0
        self.lbl_summary.setText(f"总积分: {total_pts}  平均每日: {avg:.1f}  打卡率: {rate:.0f}%")