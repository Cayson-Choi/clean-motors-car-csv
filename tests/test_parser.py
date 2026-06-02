# tests/test_parser.py
from src import parser

def test_parse_parking_csv(park_csv):
    header, data, enc = parser.parse_parking_csv(park_csv)
    assert len(header) == 2
    assert header[0][2] == '차량번호'
    assert len(data) == 3
    assert [r[2] for r in data] == ['11가1111','22나2222','33다3333']
    assert enc in ('utf-8-sig','utf-8','cp949')

def test_parse_ledger_and_additions(jesi_xlsx):
    rows = parser.parse_ledger(jesi_xlsx)
    assert len(rows) == 4
    assert rows[0]['plate'] == 'AA1'
    add = parser.extract_presented_additions(rows)
    # 제시(상사) AA1, 미이전+공란 BB2 만 추가
    assert set(add.keys()) == {'AA1','BB2'}
    assert add['AA1'] == '프로모터스'
    assert add['BB2'] == '그린자동차매매상사'

def test_ledger_all_plates(jesi_xlsx):
    rows = parser.parse_ledger(jesi_xlsx)
    assert parser.ledger_all_plates(rows) == {'AA1','BB2','CC3','DD4'}
