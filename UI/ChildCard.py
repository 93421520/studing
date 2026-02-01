from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class ChildCard(QFrame):
    def __init__(self, cid, name, points, last_date, parent=None):
        super().__init__(parent)
        self.cid = cid
        self.name = name
        self.points = points
        self.last_date = last_date
        self.setObjectName('childCard')
        self.setStyleSheet('''
            QFrame#childCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 12px;
            }
            QFrame#childCard:hover { border: 1px solid #6aa6ff; }
            QFrame#childCard QLabel { color: #333; }
            QFrame#childCard QLabel#stat { color: #666; font-size: 11px; }
            QPushButton { min-width: 60px; }
        ''')
        self.setMinimumWidth(220)
        layout = QVBoxLayout()
        header = QHBoxLayout()
        icon = QLabel()
        # use a simple colored circle pixmap as icon
        pix = QPixmap(36,36)
        pix.fill(Qt.transparent)
        from PyQt5.QtGui import QPainter, QColor
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor('#6aa6ff'))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0,0,36,36)
        p.end()
        icon.setPixmap(pix)
        header.addWidget(icon)
        title = QLabel(self.name)
        f = QFont()
        f.setPointSize(11)
        f.setBold(True)
        title.setFont(f)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        body = QVBoxLayout()
        self.lbl_points = QLabel(f"积分: {self.points}")
        body.addWidget(self.lbl_points)
        self.lbl_last = QLabel(f"最近: {self.last_date}")
        body.addWidget(self.lbl_last)
        # 小统计
        stats_layout = QHBoxLayout()
        self.lbl_completion = QLabel("完成率: -")
        self.lbl_completion.setObjectName('stat')
        self.lbl_avg7 = QLabel("7天均分: -")
        self.lbl_avg7.setObjectName('stat')
        stats_layout.addWidget(self.lbl_completion)
        stats_layout.addStretch()
        stats_layout.addWidget(self.lbl_avg7)
        body.addLayout(stats_layout)
        layout.addLayout(body)

        foot = QHBoxLayout()
        self.btn_open = QPushButton("详情")
        self.btn_open.setProperty('role','primary')
        self.btn_history = QPushButton("历史")
        self.btn_quick = QPushButton("打卡")
        foot.addWidget(self.btn_open)
        foot.addWidget(self.btn_history)
        foot.addWidget(self.btn_quick)
        layout.addLayout(foot)

        self.setLayout(layout)

    def update(self, points, last_date, completion_rate=None, avg7=None):
        self.points = points
        self.last_date = last_date
        self.lbl_points.setText(f"积分: {self.points}")
        self.lbl_last.setText(f"最近: {self.last_date}")
        if completion_rate is not None:
            self.lbl_completion.setText(f"完成率: {completion_rate*100:.0f}%")
        else:
            self.lbl_completion.setText("完成率: -")
        if avg7 is not None:
            self.lbl_avg7.setText(f"7天均分: {avg7:.1f}")
        else:
            self.lbl_avg7.setText("7天均分: -")