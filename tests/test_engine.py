# tests/test_engine.py
from datetime import date
from src import engine

def _row(plate, name=''):
    r = ['']*16
    r[0]='O'; r[1]='X'; r[2]=plate; r[4]=name
    r[5]='2026-05-01 00:00:00'; r[6]='2999-12-31 00:00:00'
    return r

def test_process_add_and_remove():
    data = [_row('11가1111','오토마트'), _row('22나2222','그린모터스'), _row('33다3333','직원용')]
    additions = {'AA1':'프로모터스', '22나2222':'그린자동차매매상사'}  # 22나2222 이미 존재 -> 추가 안함
    sold = {'33다3333'}
    outcha = {'11가1111'}
    result, summary = engine.process(data, additions, sold, outcha, date(2026,6,2))
    plates = [r[2] for r in result]
    # 11(출차)·33(매도) 삭제, 22 유지, AA1 신규추가
    assert '11가1111' not in plates
    assert '33다3333' not in plates
    assert '22나2222' in plates
    assert 'AA1' in plates
    assert summary['added'] == 1
    assert summary['sold_removed'] == 1
    assert summary['outcha_removed'] == 1
    # 신규행 값 확인
    new = [r for r in result if r[2]=='AA1'][0]
    assert new[0]=='O' and new[1]=='X' and new[4]=='프로모터스'
    assert new[5]=='2026-06-02 00:00:00'
    assert new[6]=='2999-12-31 00:00:00'


def test_detect_duplicates():
    data = [_row('A','오토마트'), _row('B','그린'), _row('A','직원용'), _row('C','x'), _row('B','그린')]
    dups = engine.detect_duplicates(data)
    # A: 2건, B: 2건(입주사명 동일), C 없음
    assert set(dups.keys()) == {'A','B'}
    assert dups['A'] == [0,2]
    assert engine.is_pure_duplicate(data, dups['B']) is True   # 입주사명 동일
    assert engine.is_pure_duplicate(data, dups['A']) is False  # 입주사명 다름
