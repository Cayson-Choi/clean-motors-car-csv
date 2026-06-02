# tests/test_parser.py
from src import parser

def test_parse_parking_csv(park_csv):
    header, data, enc = parser.parse_parking_csv(park_csv)
    assert len(header) == 2
    assert header[0][2] == '차량번호'
    assert len(data) == 3
    assert [r[2] for r in data] == ['11가1111','22나2222','33다3333']
    assert enc in ('utf-8-sig','utf-8','cp949')
