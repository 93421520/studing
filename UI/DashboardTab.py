from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from datetime import date, timedelta
from UI.ChildCard import ChildCard

class DashboardTab(QWidget):
    """卡片式显示孩子概览与快速操作"""
    def __init__(self, db, logic):
        super().__init__()
        self.db = db
        self.logic = logic
        layout = QVBoxLayout()
        header = QHBoxLayout()
        header.addWidget(QLabel("孩子概览（卡片视图）"))
        header.addStretch()
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.clicked.connect(self.refresh)
        header.addWidget(self.btn_refresh)
        self.btn_quick = QPushButton("快速打卡")
        self.btn_quick.clicked.connect(self.open_quick_dialog)
        header.addWidget(self.btn_quick)
        self.btn_snapshot = QPushButton("保存预览截图")
        self.btn_snapshot.clicked.connect(self.save_snapshot)
        header.addWidget(self.btn_snapshot)
        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        self.container.setLayout(self.grid)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        # 清空网格
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.cards = []
        cols = 3
        row = col = 0
        for cid, name in self.db.get_children():
            pts = self.db.get_points(cid)
            last = self.db.get_last_record_date(cid) or '未打卡'
            # 计算小统计
            total_tasks = len(self.db.get_plan(cid))
            today = date.today().isoformat()
            records_today = self.db.get_records(child_id=cid, start_date=today, end_date=today)
            if records_today and total_tasks>0:
                done_tasks = len(records_today[0][1])
                completion_rate = done_tasks / total_tasks
            else:
                completion_rate = 0.0
            # 7天均分
            start7 = (date.today() - timedelta(days=6)).isoformat()
            records7 = self.db.get_records(child_id=cid, start_date=start7, end_date=today)
            sum7 = sum(r[2] for r in records7)
            avg7 = sum7 / 7.0
            card = ChildCard(cid, name, pts, last)
            card.update(pts, last, completion_rate=completion_rate, avg7=avg7)
            card.btn_open.clicked.connect(lambda _, c=cid: self.open_child_by_id(c))
            card.btn_quick.clicked.connect(lambda _, c=cid: self.open_quick_for_child(c))
            card.btn_history.clicked.connect(lambda _, c=cid: self.open_history(c))
            self.grid.addWidget(card, row, col)
            self.cards.append(card)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def open_child_by_id(self, cid):
        top = self.window()
        if hasattr(top, 'open_child_window'):
            top.open_child_window(cid)

    def open_quick_for_child(self, cid):
        from UI.QuickCheckDialog import QuickCheckDialog
        dlg = QuickCheckDialog(self.db, self.logic)
        # set selected
        idx = dlg.combo.findData(cid)
        if idx >= 0:
            dlg.combo.setCurrentIndex(idx)
            dlg.load_tasks()
        if dlg.exec_():
            top = self.window()
            if hasattr(top, 'page_dashboard'):
                top.page_dashboard.refresh()
            if hasattr(top, 'page_reports'):
                top.page_reports.refresh()

    def open_quick_dialog(self):
        from UI.QuickCheckDialog import QuickCheckDialog
        dlg = QuickCheckDialog(self.db, self.logic)
        if dlg.exec_():
            top = self.window()
            if hasattr(top, 'page_dashboard'):
                top.page_dashboard.refresh()
            if hasattr(top, 'page_reports'):
                top.page_reports.refresh()

    def save_snapshot(self):
        # 保存当前 container 的截图
        pix = self.container.grab()
        path = 'dashboard_preview.png'
        pix.save(path)
        QMessageBox.information(self, '保存', f'已保存到 {path}')

    def open_history(self, cid):
        from UI.ChildHistoryDialog import ChildHistoryDialog
        dlg = ChildHistoryDialog(self.db, cid)
        dlg.exec_()