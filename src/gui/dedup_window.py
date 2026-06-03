from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QGroupBox, QRadioButton, QCheckBox, QLineEdit, QPushButton,
    QButtonGroup, QFrame, QFileDialog, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt
from src import engine
from src.gui.main_window import _make_header, _make_footer

# 선택된 행 / 미선택 행 / 모두삭제 상태의 행 스타일
STYLE_SELECTED   = 'QFrame#dupRow { background:#CDE6FF; border:1px solid #4A90D9; border-radius:5px; }'
STYLE_UNSELECTED = 'QFrame#dupRow { background:transparent; border:1px solid transparent; }'
STYLE_DELETED    = 'QFrame#dupRow { background:#F0F0F0; border:1px solid #D0D0D0; border-radius:5px; }'

NAME_COL = 4

class DedupWindow(QWidget):
    def __init__(self, header, data, summary, encoding):
        super().__init__()
        self.header, self.data, self.encoding = header, data, encoding
        self.setWindowTitle('중복 해결')
        self.resize(640, 760)
        self.setMinimumWidth(520)
        self.dups = engine.detect_duplicates(data)
        self.widgets = {}  # plate -> dict(group, radios, name_edits, delete_all)

        # ── Root layout ───────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        root.addWidget(_make_header('🚗 중복 해결', '중복 차량 처리'))

        # ── Body ──────────────────────────────────────────────────
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 24, 24, 24)
        body_lay.setSpacing(14)

        # Summary label
        s = summary
        summary_lbl = QLabel(
            f"제시추가 +{s['added']} / 매도삭제 -{s['sold_removed']} / "
            f"출차삭제 -{s['outcha_removed']} / 남은 중복 {len(self.dups)}그룹"
        )
        summary_lbl.setStyleSheet('color: #64748B; font-size: 13px;')
        body_lay.addWidget(summary_lbl)

        # Scroll area with duplicate groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        ilay = QVBoxLayout(inner)
        ilay.setSpacing(10)
        for plate, idxs in sorted(self.dups.items()):
            ilay.addWidget(self._group(plate, idxs))
        ilay.addStretch()
        scroll.setWidget(inner)
        body_lay.addWidget(scroll, 1)

        # Primary finish button (full width)
        self.btn = QPushButton('최종 CSV 생성')
        self.btn.setObjectName('primary')
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn.clicked.connect(self.finish)
        body_lay.addWidget(self.btn)

        root.addWidget(body, 1)

        # ── Footer ────────────────────────────────────────────────
        root.addWidget(_make_footer())

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
        out, _ = QFileDialog.getSaveFileName(self, '최종 CSV 저장', '일반정기차량_최종.csv', 'CSV (*.csv)')
        if not out: return
        engine.write_csv(out, self.header, final, self.encoding)
        QMessageBox.information(self, '완료', f'최종 {len(final)}대 저장 완료\n{out}')
        self.close()
