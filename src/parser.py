import csv

def detect_encoding(path):
    for enc in ('utf-8-sig', 'utf-8', 'cp949'):
        try:
            with open(path, encoding=enc) as f:
                f.read()
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return 'utf-8'

def parse_parking_csv(path):
    enc = detect_encoding(path)
    with open(path, encoding=enc, newline='') as f:
        rows = [list(r) for r in csv.reader(f)]
    header = rows[:2]
    data = [r for r in rows[2:] if len(r) > 2 and str(r[2]).strip()]
    # 길이 16으로 정규화
    for r in data:
        while len(r) < 16:
            r.append('')
    return header, data, enc
