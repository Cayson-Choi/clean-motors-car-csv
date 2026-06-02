from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QGroupBox, QRadioButton, QCheckBox, QLineEdit, QPushButton,
    QButtonGroup, QFileDialog, QMessageBox)
from src import engine

NAME_COL = 4

class DedupWindow(QWidget):
    def __init__(self, header, data, summary, encoding):
        super().__init__()
        self.header, self.data, self.encoding = header, data, encoding
        self.setWindowTitle('중복 해결')
        self.dups = engine.detect_duplicates(data)
        self.widgets = {}  # plate -> dict(group, radios, name_edits, delete_all)
        lay = QVBoxLayout(self)
        s = summary
        lay.addWidget(QLabel(
            f"제시추가 +{s['added']} / 매도삭제 -{s['sold_removed']} / "
            f"출차삭제 -{s['outcha_removed']} / 남은 중복 {len(self.dups)}그룹"))
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        inner = QWidget(); ilay = QVBoxLayout(inner)
        for plate, idxs in sorted(self.dups.items()):
            ilay.addWidget(self._group(plate, idxs))
        scroll.setWidget(inner); lay.addWidget(scroll)
        self.btn = QPushButton('최종 CSV 생성'); self.btn.clicked.connect(self.finish)
        lay.addWidget(self.btn)

    def _group(self, plate, idxs):
        box = QGroupBox(f'차량번호 {plate} ({len(idxs)}건)')
        v = QVBoxLayout(box)
        bg = QButtonGroup(box); radios=[]; edits=[]
        pure = engine.is_pure_duplicate(self.data, idxs)
        for n, i in enumerate(idxs):
            row = QHBoxLayout()
            rb = QRadioButton('남김'); bg.addButton(rb, i)
            if n == 0: rb.setChecked(True)
            name = QLineEdit(str(self.data[i][NAME_COL]))
            row.addWidget(rb); row.addWidget(QLabel('입주사명:')); row.addWidget(name)
            v.addLayout(row); radios.append(rb); edits.append((i, name))
        chk = QCheckBox('둘 다(모두) 삭제'); v.addWidget(chk)
        self.widgets[plate] = {'bg': bg, 'edits': edits, 'delete_all': chk}
        return box

    def _resolutions(self):
        res = {}
        for plate, w in self.widgets.items():
            if w['delete_all'].isChecked():
                res[plate] = {'delete_all': True}; continue
            keep = w['bg'].checkedId()
            entry = {'keep_index': keep}
            for i, edit in w['edits']:
                if i == keep:
                    if edit.text().strip() != str(self.data[i][NAME_COL]).strip():
                        entry['new_name'] = edit.text().strip()
            res[plate] = entry
        return res

    def finish(self):
        final = engine.apply_resolution(self.data, self._resolutions())
        out,_ = QFileDialog.getSaveFileName(self,'최종 CSV 저장','일반정기차량_최종.csv','CSV (*.csv)')
        if not out: return
        engine.write_csv(out, self.header, final, self.encoding)
        QMessageBox.information(self,'완료', f'최종 {len(final)}대 저장 완료\n{out}')
        self.close()
