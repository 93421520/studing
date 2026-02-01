from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from UI.DashboardTab import DashboardTab
from UI.ReportsTab import ReportsTab
from UI.ChildTab import ChildTab

class MainWindow(QMainWindow):
    def __init__(self, db, logic):
        super().__init__()
        self.db = db
        self.logic = logic
        self.setWindowTitle("上海家长助手 - 主面板")
        self.resize(1000, 700)

        # 左侧导航
        self.side = QListWidget()
        self.side.addItem("仪表盘")
        self.side.addItem("孩子管理")
        self.side.addItem("学习计划")
        self.side.addItem("报表")
        self.side.setFixedWidth(150)
        self.side.currentRowChanged.connect(self.switch_page)

        # 右侧页面（堆栈）
        self.stack = QStackedWidget()
        self.page_dashboard = DashboardTab(self.db, self.logic)
        from UI.ChildrenTab import ChildrenTab
        from UI.PlansTab import PlansTab
        self.page_children = ChildrenTab(self.db)
        self.page_plans = PlansTab(self.db)

        self.page_reports = ReportsTab(self.db)

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_children)
        self.stack.addWidget(self.page_plans)
        self.stack.addWidget(self.page_reports)

        central = QHBoxLayout()
        central.addWidget(self.side)
        central.addWidget(self.stack)
        container = QWidget()
        container.setLayout(central)
        self.setCentralWidget(container)

        # 默认选中仪表盘
        self.side.setCurrentRow(0)

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)

    def open_manage_dialog(self):
        from UI.ManageChildrenDialog import ManageChildrenDialog
        dlg = ManageChildrenDialog(self.db)
        if dlg.exec_():
            # 刷新仪表盘数据
            self.page_dashboard.refresh()
            self.page_reports.refresh()

    def open_child_window(self, child_id):
        # 打开单独的孩子窗口（孩子端受限模式）
        name = self.db.cursor.execute("SELECT name FROM children WHERE id=?", (child_id,)).fetchone()[0]
        win = QMainWindow()
        win.setWindowTitle("孩子端 - " + name)
        child_tab = ChildTab(child_id, name, self.db, self.logic, restricted=True)
        win.setCentralWidget(child_tab)
        win.resize(600, 400)
        win.show()
        # 保持窗口引用
        if not hasattr(self, 'child_windows'):
            self.child_windows = []
        self.child_windows.append(win)