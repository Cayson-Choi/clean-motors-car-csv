from datetime import date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QDateEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import QDate, Signal
from src import parser, engine

class MainWindow(QWidget):
    processed = Signal(object, object, object, object)  # header, data, summary, encoding

    def __init__(self):
        super().__init__()
        self.setWindowTitle('정기차량 관리 자동화')
        self.park = self.maedo = self.jesi = None
        self.outcha = []
        lay = QVBoxLayout(self)
        self.lbl_park = QLabel('일반정기차량 CSV: (없음)')
        self.lbl_maedo = QLabel('매도기록대장: (없음)')
        self.lbl_jesi = QLabel('제시기록대장: (없음)')
        for lbl, btn_text, slot in [
            (self.lbl_park, '일반정기차량 CSV 선택', self.pick_park),
            (self.lbl_maedo, '매도기록대장 선택', self.pick_maedo),
            (self.lbl_jesi, '제시기록대장 선택', self.pick_jesi)]:
            row = QHBoxLayout(); b = QPushButton(btn_text); b.clicked.connect(slot)
            row.addWidget(b); row.addWidget(lbl); lay.addLayout(row)
        lay.addWidget(QLabel('오토넷출차리스트 (여러 개)'))
        self.list_outcha = QListWidget(); lay.addWidget(self.list_outcha)
        orow = QHBoxLayout()
        b_add = QPushButton('+ 추가'); b_add.clicked.connect(self.add_outcha)
        b_del = QPushButton('선택 제거'); b_del.clicked.connect(self.del_outcha)
        orow.addWidget(b_add); orow.addWidget(b_del); lay.addLayout(orow)
        drow = QHBoxLayout(); drow.addWidget(QLabel('기준일(유효일시):'))
        self.date = QDateEdit(QDate.currentDate()); self.date.setDisplayFormat('yyyy-MM-dd')
        drow.addWidget(self.date); lay.addLayout(drow)
        self.btn_run = QPushButton('처리 시작'); self.btn_run.clicked.connect(self.run)
        lay.addWidget(self.btn_run)

    def pick_park(self):
        f,_ = QFileDialog.getOpenFileName(self,'일반정기차량 CSV','','CSV (*.csv)')
        if f: self.park=f; self.lbl_park.setText(f'일반정기차량 CSV: {f}')
    def pick_maedo(self):
        f,_ = QFileDialog.getOpenFileName(self,'매도기록대장','','Excel (*.xlsx)')
        if f: self.maedo=f; self.lbl_maedo.setText(f'매도기록대장: {f}')
    def pick_jesi(self):
        f,_ = QFileDialog.getOpenFileName(self,'제시기록대장','','Excel (*.xlsx)')
        if f: self.jesi=f; self.lbl_jesi.setText(f'제시기록대장: {f}')
    def add_outcha(self):
        fs,_ = QFileDialog.getOpenFileNames(self,'오토넷출차리스트','','Excel (*.xlsx)')
        for f in fs:
            if f not in self.outcha:
                self.outcha.append(f); self.list_outcha.addItem(f)
    def del_outcha(self):
        for it in self.list_outcha.selectedItems():
            self.outcha.remove(it.text()); self.list_outcha.takeItem(self.list_outcha.row(it))

    def run(self):
        if not (self.park and self.maedo and self.jesi):
            QMessageBox.warning(self,'경고','일반정기차량/매도/제시 파일을 모두 선택하세요.'); return
        d = self.date.date(); base = date(d.year(), d.month(), d.day())
        header, data, enc = parser.parse_parking_csv(self.park)
        jesi_rows = parser.parse_ledger(self.jesi)
        additions = parser.extract_presented_additions(jesi_rows)
        sold = parser.ledger_all_plates(parser.parse_ledger(self.maedo))
        outcha = parser.parse_outcha_many(self.outcha)
        result, summary = engine.process(data, additions, sold, outcha, base)
        self.processed.emit(header, result, summary, enc)
