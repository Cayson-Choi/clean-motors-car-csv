from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QGroupBox, QRadioButton, QCheckBox, QLineEdit, QPushButton,
    QButtonGroup, QFrame, QFileDialog, QMessageBox)
from src import engine

# 선택된 행 / 미선택 행 / 모두삭제 상태의 행 스타일
STYLE_SELECTED = 'QFrame#dupRow { background:#CDE6FF; border:1px solid #4A90D9; border-radius:5px; }'
STYLE_UNSELECTED = 'QFrame#dupRow { background:transparent; border:1px solid transparent; }'
STYLE_DELETED = 'QFrame#dupRow { background:#F0F0F0; border:1px solid #D0D0D0; border-radius:5px; }'

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
        bg = QButtonGroup(box); edits = []; frames = []
        chk = QCheckBox('둘 다(모두) 삭제')
        for n, i in enumerate(idxs):
            frame = QFrame(); frame.setObjectName('dupRow')
            row = QHBoxLayout(frame); row.setContentsMargins(6, 3, 6, 3)
            rb = QRadioButton('남김'); bg.addButton(rb, i)
            name = QLineEdit(str(self.data[i][NAME_COL]))
            row.addWidget(rb); row.addWidget(QLabel('입주사명:')); row.addWidget(name, 1)
            v.addWidget(frame)
            edits.append((i, name)); frames.append((rb, frame))
            if n == 0: rb.setChecked(True)
        v.addWidget(chk)

        def refresh():
            delete_all = chk.isChecked()
            for rb, frame in frames:
                if delete_all:
                    frame.setStyleSheet(STYLE_DELETED); rb.setText('남김')
                elif rb.isChecked():
                    frame.setStyleSheet(STYLE_SELECTED); rb.setText('★ 남김 (선택됨)')
                else:
                    frame.setStyleSheet(STYLE_UNSELECTED); rb.setText('남김')

        for rb, _f in frames:
            rb.toggled.connect(refresh)
        chk.toggled.connect(refresh)
        refresh()

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
