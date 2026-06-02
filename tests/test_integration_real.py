import os
import pytest
from datetime import date
from src import parser, engine

BASE = r'D:\Antigravity\excel-work\0602'
park = os.path.join(BASE, '일반정기차량26.6.2.csv')


@pytest.mark.skipif(not os.path.exists(park), reason='real data not present')
def test_real_data_counts():
    header, data, enc = parser.parse_parking_csv(park)
    jesi = parser.parse_ledger(os.path.join(BASE, '06월01일기준 제시기록대장.xlsx'))
    additions = parser.extract_presented_additions(jesi)
    sold = parser.ledger_all_plates(
        parser.parse_ledger(os.path.join(BASE, '06월01일기준 매도기록대장.xlsx'))
    )
    outcha = parser.parse_outcha_many([
        os.path.join(BASE, '26-01오토넷출차리스트.xlsx'),
        os.path.join(BASE, '26-02오토넷출차리스트.xlsx'),
        os.path.join(BASE, '26-03오토넷출차리스트.xlsx'),
        os.path.join(BASE, '26-04월출차리스트.xlsx'),
    ])
    result, summary = engine.process(data, additions, sold, outcha, date(2026, 6, 2))
    assert summary['sold_removed'] == 19
    assert summary['outcha_removed'] == 116
    assert summary['added'] == 4
    assert len(result) == 519
