import csv
import pytest

PARK_HEADER = ['유효','VIP','차량번호','입주사아이디','입주사명','유효일시','만료일시',
               '정기권명','월정액','결제금액','비고','부서명','이름','전화번호','메모','수정일시']
PARK_NOTE = ['(O:추가 X:삭제)','(생략)','(필수)','(생략)','(선택)','(필수)','(필수)',
             '(사용안함)','(사용안함)','(사용안함)','(생략)','(선택)','(선택)','(선택)','(선택)','(생략)']

def _row(plate, name=''):
    r = ['']*16
    r[0]='O'; r[1]='X'; r[2]=plate; r[4]=name
    r[5]='2026-05-01 00:00:00'; r[6]='2999-12-31 00:00:00'
    return r

@pytest.fixture
def park_csv(tmp_path):
    p = tmp_path / 'park.csv'
    rows = [PARK_HEADER, PARK_NOTE, _row('11가1111','오토마트'),
            _row('22나2222','그린모터스'), _row('33다3333','직원용')]
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        csv.writer(f).writerows(rows)
    return str(p)
