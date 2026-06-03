import os
from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QDateEdit, QFileDialog, QMessageBox,
    QAbstractItemView, QFrame, QSizePolicy, QSpacerItem,
)
from PySide6.QtCore import QDate, Signal, Qt

from src import parser, engine


def _make_header(title: str, subtitle: str) -> QFrame:
    """Return the navy header bar frame."""
    bar = QFrame()
    bar.setObjectName('header')
    bar.setFixedHeight(64)
    lay = QHBoxLayout(bar)
    lay.setContentsMargins(16, 0, 16, 0)
    lay.setSpacing(8)

    left = QVBoxLayout()
    left.setSpacing(2)
    lbl_title = QLabel(title)
    lbl_title.setObjectName('title')
    lbl_sub = QLabel(subtitle)
    lbl_sub.setObjectName('subtitle')
    left.addWidget(lbl_title)
    left.addWidget(lbl_sub)

    lay.addLayout(left)
    lay.addStretch()
    return bar


def _make_footer() -> QFrame:
    """Return the copyright footer frame."""
    bar = QFrame()
    bar.setObjectName('footer')
    bar.setFixedHeight(32)
    lay = QHBoxLayout(bar)
    lay.setContentsMargins(12, 0, 12, 0)
    lbl = QLabel('© 2026 깨끗한 모터스.  All Rights Reserved.')
    lbl.setObjectName('footer_text')
    lbl.setAlignment(Qt.AlignCenter)
    lay.addWidget(lbl)
    return bar


class MainWindow(QWidget):
    processed = Signal(object, object, object, object)  # header, data, summary, encoding

    def __init__(self):
        super().__init__()
        self.setWindowTitle('정기차량 관리 자동화')
        self.resize(560, 720)
        self.setMinimumWidth(520)

        self.park = self.maedo = self.jesi = None
        self.outcha: list = []

        # ── Root layout (no margins — header/footer touch edges) ──
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 1. Header ─────────────────────────────────────────────
        root.addWidget(_make_header('🚗 정기차량 관리 자동화', '일반정기차량 갱신 도구'))

        # ── 2. Body ───────────────────────────────────────────────
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 24, 24, 24)
        body_lay.setSpacing(14)

        # Card
        card = QFrame()
        card.setObjectName('card')
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(20, 20, 20, 20)
        card_lay.setSpacing(12)

        # File pick rows
        file_specs = [
            ('일반정기차량 CSV', '...선택', self.pick_park),
            ('매도기록대장', '...선택', self.pick_maedo),
            ('제시기록대장', '...선택', self.pick_jesi),
        ]
        self.lbl_park = QLabel('(없음)')
        self.lbl_maedo = QLabel('(없음)')
        self.lbl_jesi = QLabel('(없음)')
        status_labels = [self.lbl_park, self.lbl_maedo, self.lbl_jesi]

        for (field_name, btn_text, slot), status_lbl in zip(file_specs, status_labels):
            row = QHBoxLayout()
            row.setSpacing(8)

            name_lbl = QLabel(field_name)
            name_lbl.setFixedWidth(120)
            name_lbl.setStyleSheet('font-weight: 600;')

            btn = QPushButton(btn_text)
            btn.clicked.connect(slot)
            btn.setFixedWidth(88)

            status_lbl.setStyleSheet('color: #64748B;')
            status_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            row.addWidget(name_lbl)
            row.addWidget(btn)
            row.addWidget(status_lbl, 1)
            card_lay.addLayout(row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        card_lay.addWidget(sep)

        # Outcha list
        outcha_title = QLabel('오토넷출차리스트 (여러 개)')
        outcha_title.setStyleSheet('font-weight: 600;')
        card_lay.addWidget(outcha_title)

        self.list_outcha = QListWidget()
        self.list_outcha.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_outcha.setMinimumHeight(120)
        card_lay.addWidget(self.list_outcha)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        b_add = QPushButton('+ 추가')
        b_add.clicked.connect(self.add_outcha)
        b_del = QPushButton('선택 제거')
        b_del.clicked.connect(self.del_outcha)
        btn_row.addWidget(b_add)
        btn_row.addWidget(b_del)
        btn_row.addStretch()
        card_lay.addLayout(btn_row)

        # Separator 2
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        card_lay.addWidget(sep2)

        # Date row
        date_row = QHBoxLayout()
        date_row.setSpacing(8)
        date_lbl = QLabel('기준일(유효일시)')
        date_lbl.setStyleSheet('font-weight: 600;')
        date_lbl.setFixedWidth(120)
        self.date = QDateEdit(QDate.currentDate())
        self.date.setDisplayFormat('yyyy-MM-dd')
        self.date.setMinimumHeight(36)
        self.date.setMinimumWidth(160)
        self.date.setCalendarPopup(True)
        date_row.addWidget(date_lbl)
        date_row.addWidget(self.date)
        date_row.addStretch()
        card_lay.addLayout(date_row)

        body_lay.addWidget(card)

        # ── 3. Primary run button ──────────────────────────────────
        self.btn_run = QPushButton('처리 시작')
        self.btn_run.setObjectName('primary')
        self.btn_run.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_run.clicked.connect(self.run)
        body_lay.addWidget(self.btn_run)

        body_lay.addStretch()
        root.addWidget(body, 1)

        # ── 4. Footer ──────────────────────────────────────────────
        root.addWidget(_make_footer())

    # ── File pickers ──────────────────────────────────────────────
    def pick_park(self):
        f, _ = QFileDialog.getOpenFileName(self, '일반정기차량 CSV', '', 'CSV (*.csv)')
        if f:
            self.park = f
            self.lbl_park.setText(os.path.basename(f))
            self.lbl_park.setStyleSheet('color: #1E293B;')

    def pick_maedo(self):
        f, _ = QFileDialog.getOpenFileName(self, '매도기록대장', '', 'Excel (*.xlsx)')
        if f:
            self.maedo = f
            self.lbl_maedo.setText(os.path.basename(f))
            self.lbl_maedo.setStyleSheet('color: #1E293B;')

    def pick_jesi(self):
        f, _ = QFileDialog.getOpenFileName(self, '제시기록대장', '', 'Excel (*.xlsx)')
        if f:
            self.jesi = f
            self.lbl_jesi.setText(os.path.basename(f))
            self.lbl_jesi.setStyleSheet('color: #1E293B;')

    def add_outcha(self):
        fs, _ = QFileDialog.getOpenFileNames(self, '오토넷출차리스트', '', 'Excel (*.xlsx)')
        for f in fs:
            if f not in self.outcha:
                self.outcha.append(f)
                self.list_outcha.addItem(f)

    def del_outcha(self):
        rows = sorted(
            (self.list_outcha.row(it) for it in self.list_outcha.selectedItems()),
            reverse=True,
        )
        for r in rows:
            it = self.list_outcha.takeItem(r)
            self.outcha.remove(it.text())

    def run(self):
        if not (self.park and self.maedo and self.jesi):
            QMessageBox.warning(self, '경고', '일반정기차량/매도/제시 파일을 모두 선택하세요.')
            return
        d = self.date.date()
        base = date(d.year(), d.month(), d.day())
        header, data, enc = parser.parse_parking_csv(self.park)
        jesi_rows = parser.parse_ledger(self.jesi)
        additions = parser.extract_presented_additions(jesi_rows)
        sold = parser.ledger_all_plates(parser.parse_ledger(self.maedo))
        outcha = parser.parse_outcha_many(self.outcha)
        result, summary = engine.process(data, additions, sold, outcha, base)
        self.processed.emit(header, result, summary, enc)
