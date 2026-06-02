# tests/test_parser.py
import os
import pytest
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

def test_parse_outcha(outcha_a, outcha_b):
    a = parser.parse_outcha(outcha_a)
    assert a == {'22나2222','99바9999'}
    b = parser.parse_outcha(outcha_b)
    assert b == {'77사7777'}

def test_parse_outcha_many(outcha_a, outcha_b):
    s = parser.parse_outcha_many([outcha_a, outcha_b])
    assert s == {'22나2222','99바9999','77사7777'}

def test_detect_encoding_utf8_bom(tmp_path):
    p = tmp_path / 'bom.csv'
    p.write_bytes(b'\xef\xbb\xbf' + '안녕하세요'.encode('utf-8'))
    assert parser.detect_encoding(str(p)) == 'utf-8-sig'

def test_detect_encoding_utf8_no_bom(tmp_path):
    p = tmp_path / 'plain.csv'
    p.write_bytes('안녕하세요'.encode('utf-8'))
    assert parser.detect_encoding(str(p)) == 'utf-8'

def test_detect_encoding_cp949(tmp_path):
    p = tmp_path / 'cp949.csv'
    p.write_bytes('안녕하세요'.encode('cp949'))
    assert parser.detect_encoding(str(p)) == 'cp949'
