from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class StartLoginDialog(QDialog):
    """支持数据库校验的登录窗口"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_info = None  # 存储登录结果 ('parent', None) 或 ('child', child_id)
        self.setWindowTitle('系统登录')
        self.setMinimumWidth(380)
        
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # --- 家长登录页 ---
        self.parent_tab = QWidget()
        p_layout = QFormLayout()
        self.parent_pwd = QLineEdit()
        self.parent_pwd.setPlaceholderText("请输入家长管理密码")
        self.parent_pwd.setEchoMode(QLineEdit.Password)
        p_layout.addRow('家长密码:', self.parent_pwd)
        self.parent_tab.setLayout(p_layout)

        # --- 孩子登录页 ---
        self.child_tab = QWidget()
        c_layout = QFormLayout()
        self.child_combo = QComboBox()
        # 从数据库加载孩子列表 (假设 role='child')
        self.db.cursor.execute("SELECT id, name FROM users WHERE role='child'")
        for cid, name in self.db.cursor.fetchall():
            self.child_combo.addItem(name, cid)
        
        c_layout.addRow('选择孩子:', self.child_combo)
        # 孩子端这里可以根据需要加密码，目前保持简洁
        self.child_tab.setLayout(c_layout)

        self.tabs.addTab(self.parent_tab, "家长入口")
        self.tabs.addTab(self.child_tab, "孩子入口")
        layout.addWidget(self.tabs)

        btns = QHBoxLayout()
        self.btn_login = QPushButton("登录")
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_login)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.setLayout(layout)

    def handle_login(self):
        idx = self.tabs.currentIndex()
        if idx == 0:  # 家长登录
            input_pwd = self.parent_pwd.text()
            correct_pwd = self.db.get_parent_password()
            if input_pwd == correct_pwd:
                self.user_info = ('parent', None)
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "家长密码不正确！")
        else:  # 孩子登录
            cid = self.child_combo.currentData()
            name = self.child_combo.currentText()
            if cid:
                self.user_info = ('child', cid)
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "请先添加孩子信息")

    def exec_and_get_user(self):
        if self.exec_():
            return self.user_info
        return None