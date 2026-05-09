import csv
from itertools import combinations
from pathlib import Path

CSV_PATH = Path(__file__).parent / "valuation.csv"
THRESHOLD = 10_00_000


def parse_inr(s: str) -> int:
    return int(s.replace(",", "").strip())


def fmt_inr(n: int) -> str:
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)
    return ",".join(reversed(parts)) + "," + last3


properties = []
with CSV_PATH.open(newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        sno, name, value = row[0].strip(), row[1].strip(), row[2].strip()
        if not sno or name.upper() == "GRAND TOTAL":
            continue
        properties.append((name, parse_inr(value)))

n = len(properties)
total = sum(v for _, v in properties)

results = []
seen = set()

for r in range(0, n + 1):
    for combo in combinations(properties, r):
        a_names = frozenset(name for name, _ in combo)
        b_names = frozenset(name for name, _ in properties) - a_names
        key = frozenset([a_names, b_names])
        if key in seen:
            continue
        seen.add(key)
        sum_a = sum(v for _, v in combo)
        sum_b = total - sum_a
        diff = abs(sum_a - sum_b)
        if diff <= THRESHOLD:
            order = {name: i for i, (name, _) in enumerate(properties)}
            a_sorted = sorted(a_names, key=lambda x: order[x])
            b_sorted = sorted(b_names, key=lambda x: order[x])
            results.append((diff, a_sorted, sum_a, b_sorted, sum_b))

results.sort(key=lambda x: x[0])

print(f"Total valuation: Rs. {fmt_inr(total)}")
print(f"Threshold (max difference): Rs. {fmt_inr(THRESHOLD)}")
print(f"Found {len(results)} divisions within threshold\n")

col_a = 60
col_b = 60
header = (
    f"{'#':>3}  {'Group A':<{col_a}} {'Sum A (Rs.)':>15}  "
    f"{'Group B':<{col_b}} {'Sum B (Rs.)':>15}  {'Diff (Rs.)':>12}"
)
print(header)
print("-" * len(header))
for idx, (diff, a, sa, b, sb) in enumerate(results, 1):
    a_str = ", ".join(a)
    b_str = ", ".join(b)
    print(
        f"{idx:>3}  {a_str:<{col_a}} {fmt_inr(sa):>15}  "
        f"{b_str:<{col_b}} {fmt_inr(sb):>15}  {fmt_inr(diff):>12}"
    )
