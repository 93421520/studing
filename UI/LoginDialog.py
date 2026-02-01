from PyQt5.QtWidgets import *

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected = None
        self.setWindowTitle("孩子登录")
        layout = QVBoxLayout()
        self.combo = QComboBox()
        self.mapping = {}
        for cid,name in db.get_children():
            self.combo.addItem(name)
            self.mapping[name] = cid
        layout.addWidget(self.combo)
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd)
        btns = QHBoxLayout()
        login = QPushButton("登录")
        login.clicked.connect(self.try_login)
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        btns.addWidget(login); btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def try_login(self):
        name = self.combo.currentText()
        cid = self.mapping[name]
        pwd = self.pwd.text()
        if self.db.check_password(cid, pwd):
            self.selected = cid
            self.accept()
        else:
            QMessageBox.warning(self, "失败", "密码错误或未设置")

    def exec_and_get_child(self):
        if self.exec_():
            return self.selected
        return None