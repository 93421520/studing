from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class StartLoginDialog(QDialog):
    """启动登录：家长或孩子登录"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user = None  # ('parent', None) 或 ('child', child_id)
        self.setWindowTitle('登录')
        self.setMinimumWidth(360)
        layout = QVBoxLayout()

        tabs = QTabWidget()
        # 家长登录
        p_tab = QWidget()
        p_layout = QFormLayout()
        self.parent_user = QLineEdit('admin')
        self.parent_pwd = QLineEdit('123456')
        self.parent_pwd.setEchoMode(QLineEdit.Password)
        p_layout.addRow('用户名', self.parent_user)
        p_layout.addRow('密码', self.parent_pwd)
        p_tab.setLayout(p_layout)
        tabs.addTab(p_tab, '家长')

        # 孩子登录（和之前 LoginDialog 类似）
        c_tab = QWidget()
        c_layout = QVBoxLayout()
        form = QFormLayout()
        self.combo = QComboBox()
        self.mapping = {}
        for cid, name in self.db.get_children():
            self.combo.addItem(name, cid)
            self.mapping[name] = cid
        form.addRow('孩子', self.combo)
        self.child_pwd = QLineEdit('123456')
        self.child_pwd.setEchoMode(QLineEdit.Password)
        form.addRow('密码', self.child_pwd)
        c_layout.addLayout(form)
        c_tab.setLayout(c_layout)
        tabs.addTab(c_tab, '孩子')

        layout.addWidget(tabs)

        btns = QHBoxLayout()
        login = QPushButton('登录')
        login.clicked.connect(lambda: self.try_login(tabs.currentIndex()))
        cancel = QPushButton('取消')
        cancel.clicked.connect(self.reject)
        btns.addWidget(login)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def try_login(self, tab_index):
        if tab_index == 0:
            # parent
            user = self.parent_user.text().strip()
            pwd = self.parent_pwd.text()
            # 简单校验：默认账号 admin / 密码 123456
            if user == 'admin' and pwd == '123456':
                self.user = ('parent', None)
                self.accept()
            else:
                QMessageBox.warning(self, '登录失败', '用户名或密码错误')
        else:
            # child
            name = self.combo.currentText()
            if not name:
                QMessageBox.warning(self, '错误', '没有可用的孩子，请联系家长添加')
                return
            cid = self.combo.currentData()
            pwd = self.child_pwd.text()
            if self.db.check_password(cid, pwd):
                self.user = ('child', cid)
                self.accept()
            else:
                QMessageBox.warning(self, '登录失败', '密码错误或未设置')

    def exec_and_get_user(self):
        if self.exec_():
            return self.user
        return None