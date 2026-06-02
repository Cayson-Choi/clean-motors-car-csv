import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PySide6.QtWidgets import QApplication
from src.gui.dedup_window import DedupWindow


@pytest.fixture(scope='session')
def qapp():
    return QApplication.instance() or QApplication([])


def _row(p, n):
    r = [''] * 16
    r[0] = 'O'; r[1] = 'X'; r[2] = p; r[4] = n
    return r


def _win(qapp):
    data = [_row('A', '오토마트'), _row('A', '직원용')]
    header = [['유효', 'VIP', '차량번호'] + [''] * 13, [''] * 16]
    return DedupWindow(header, data, {'added': 0, 'sold_removed': 0, 'outcha_removed': 0}, 'utf-8-sig')


def test_default_first_row_selected_and_highlighted(qapp):
    w = _win(qapp)
    btns = w.widgets['A']['bg'].buttons()
    assert btns[0].isChecked() and not btns[1].isChecked()
    assert 'CDE6FF' in btns[0].parentWidget().styleSheet()        # 선택 행 강조
    assert 'CDE6FF' not in btns[1].parentWidget().styleSheet()    # 미선택 행 비강조


def test_highlight_moves_on_change(qapp):
    w = _win(qapp)
    btns = w.widgets['A']['bg'].buttons()
    btns[1].setChecked(True)
    assert 'CDE6FF' not in btns[0].parentWidget().styleSheet()
    assert 'CDE6FF' in btns[1].parentWidget().styleSheet()


def test_delete_all_clears_highlight(qapp):
    w = _win(qapp)
    btns = w.widgets['A']['bg'].buttons()
    w.widgets['A']['delete_all'].setChecked(True)
    for b in btns:
        assert 'CDE6FF' not in b.parentWidget().styleSheet()
