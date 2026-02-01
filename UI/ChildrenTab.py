from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class ChildrenTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout()
        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self.on_select)
        layout.addWidget(self.list)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        form.addRow("姓名", self.name_edit)
        form.addRow("密码 (可选)", self.pwd_edit)
        layout.addLayout(form)

        btns = QHBoxLayout()
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_child)
        del_btn = QPushButton("删除选中")
        del_btn.clicked.connect(self.delete_child)
        setpwd_btn = QPushButton("设置密码")
        setpwd_btn.clicked.connect(self.set_password)
        edit_plan_btn = QPushButton("编辑学习计划")
        edit_plan_btn.clicked.connect(self.edit_plan)
        btns.addWidget(add_btn); btns.addWidget(del_btn); btns.addWidget(setpwd_btn); btns.addWidget(edit_plan_btn)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.list.clear()
        for cid, name in self.db.get_children():
            self.list.addItem(f"{cid}: {name}")

    def add_child(self):
        name = self.name_edit.text().strip()
        pwd = self.pwd_edit.text().strip() or None
        if not name:
            QMessageBox.warning(self, "错误", "请输入名字")
            return
        cid = self.db.add_child(name, password=pwd)
        if cid:
            self.refresh()
            self.name_edit.clear()
            self.pwd_edit.clear()
            QMessageBox.information(self, "完成", "孩子已添加")
        else:
            QMessageBox.warning(self, "错误", "添加失败（可能已存在）")

    def delete_child(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "请选择要删除的孩子")
            return
        cid = int(item.text().split(":")[0])
        reply = QMessageBox.question(self, "确认", "确定删除该孩子及其所有数据吗？", QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_child(cid)
            self.refresh()
            QMessageBox.information(self, "完成", "已删除")

    def set_password(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "请选择一个孩子")
            return
        cid = int(item.text().split(":")[0])
        pwd, ok = QInputDialog.getText(self, "设置密码", "输入新密码：", QLineEdit.Password)
        if ok:
            self.db.set_password(cid, pwd)
            QMessageBox.information(self, "完成", "密码已设置")

    def edit_plan(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "请选择一个孩子")
            return
        cid = int(item.text().split(":")[0])
        from UI.EditPlanDialog import EditPlanDialog
        dlg = EditPlanDialog(cid, self.db)
        if dlg.exec_():
            QMessageBox.information(self, "完成", "学习计划已更新")

    def on_select(self):
        pass