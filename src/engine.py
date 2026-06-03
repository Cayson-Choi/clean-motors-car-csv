import csv
from collections import defaultdict

PLATE_COL = 2
NAME_COL = 4


def make_row(plate, dealer, base_date, ncols=16):
    row = [''] * ncols
    row[0] = 'O'
    row[1] = 'X'
    row[2] = plate
    row[4] = dealer
    row[5] = base_date.strftime('%Y-%m-%d')
    row[6] = '2999-12-31'
    return row


def _plate(row):
    return str(row[PLATE_COL]).strip()


def process(data, additions, sold, outcha, base_date):
    remove = set(sold) | set(outcha)
    existing = set(_plate(r) for r in data)
    kept = [r for r in data if _plate(r) not in remove]
    new_rows = []
    for plate, dealer in sorted(additions.items()):
        if plate in existing or plate in remove:
            continue
        new_rows.append(make_row(plate, dealer, base_date))
    result = kept + new_rows
    summary = {
        'added': len(new_rows),
        'sold_removed': len(existing & set(sold)),
        # 매도와 출차에 동시에 있는 차량은 매도로 분류(매도를 먼저 제거하는 수동 절차와 일치)
        'outcha_removed': len((existing & set(outcha)) - set(sold)),
    }
    return result, summary


def detect_duplicates(data):
    m = defaultdict(list)
    for i, row in enumerate(data):
        m[_plate(row)].append(i)
    return {p: idxs for p, idxs in m.items() if len(idxs) > 1}


def is_pure_duplicate(data, idxs):
    names = {str(data[i][NAME_COL]).strip() for i in idxs}
    return len(names) == 1


def apply_resolution(data, resolutions):
    drop = set()
    rename = {}
    for plate, res in resolutions.items():
        idxs = [i for i, r in enumerate(data) if _plate(r) == plate]
        if res.get('delete_all'):
            drop.update(idxs)
            continue
        keep = res.get('keep_index')
        for i in idxs:
            if i != keep:
                drop.add(i)
        if keep is not None and res.get('new_name') is not None:
            rename[keep] = res['new_name']
    final = []
    for i, row in enumerate(data):
        if i in drop:
            continue
        if i in rename:
            row = list(row)
            row[NAME_COL] = rename[i]
        final.append(row)
    return final


def write_csv(path, header_rows, data_rows, encoding):
    with open(path, 'w', encoding=encoding, newline='') as f:
        w = csv.writer(f)
        for r in header_rows:
            w.writerow(r)
        for r in data_rows:
            w.writerow(r)
