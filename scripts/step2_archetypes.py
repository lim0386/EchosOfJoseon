import csv
import math

# 왕대별 실록 코드 -> 왕 이름 및 실제 재위 연수(Tk) 매핑
REIGN_INFO = {
    "waa": ("태조 (Taejo)", 1392, 1398, 7),
    "wba": ("정종 (Jeongjong)", 1398, 1400, 3),
    "wca": ("태종 (Taejong)", 1400, 1418, 19),
    "wda": ("세종 (Sejong)", 1418, 1450, 33),
    "wea": ("문종 (Munjong)", 1450, 1452, 3),
    "wfa": ("단종 (Danjong)", 1452, 1455, 4),
    "wga": ("세조 (Sejo)", 1455, 1468, 14),
    "wha": ("예종 (Yejong)", 1468, 1469, 2),
    "wia": ("성종 (Seongjong)", 1469, 1494, 26),
    "wja": ("연산군 (Yeonsangun)", 1494, 1506, 13),
    "wka": ("중종 (Jungjong)", 1506, 1544, 39),
    "wla": ("인종 (Injong)", 1544, 1545, 2),
    "wma": ("명종 (Myeongjong)", 1545, 1567, 23),
    "wna": ("선조 (Seonjo)", 1567, 1608, 42),
    "wnb": ("선조 (Seonjo)", 1567, 1608, 42),  # 선조수정실록 통합
    "woa": ("광해군 (Gwanghaegun)", 1608, 1623, 16),
    "wob": ("광해군 (Gwanghaegun)", 1608, 1623, 16),
    "wpa": ("인조 (Injo)", 1623, 1649, 27),
    "wqa": ("효종 (Hyojong)", 1649, 1659, 11),
    "wra": ("현종 (Hyeonjong)", 1659, 1674, 16),
    "wrb": ("현종 (Hyeonjong)", 1659, 1674, 16),  # 현종개수실록 통합
    "wsa": ("숙종 (Sukjong)", 1674, 1720, 47),
    "wsb": ("숙종 (Sukjong)", 1674, 1720, 47),
    "wta": ("경종 (Gyeongjong)", 1720, 1724, 5),
    "wtb": ("경종 (Gyeongjong)", 1720, 1724, 5),
    "wua": ("영조 (Yeongjo)", 1724, 1776, 53),
    "wva": ("정조 (Jeongjo)", 1776, 1800, 25),
    "wwa": ("순조 (Sunjo)", 1800, 1834, 35),
    "wxa": ("헌종 (Heonjong)", 1834, 1849, 16),
    "wya": ("철종 (Cheoljong)", 1849, 1863, 15),
    "wza": ("고종 (Gojong)", 1863, 1907, 45),
    "wzb": ("순종 (Sunjong)", 1907, 1910, 4),
}

REIGN_ORDER = [
    "태조 (Taejo)", "정종 (Jeongjong)", "태종 (Taejong)", "세종 (Sejong)", "문종 (Munjong)",
    "단종 (Danjong)", "세조 (Sejo)", "예종 (Yejong)", "성종 (Seongjong)", "연산군 (Yeonsangun)",
    "중종 (Jungjong)", "인종 (Injong)", "명종 (Myeongjong)", "선조 (Seonjo)", "광해군 (Gwanghaegun)",
    "인조 (Injo)", "효종 (Hyojong)", "현종 (Hyeonjong)", "숙종 (Sukjong)", "경종 (Gyeongjong)",
    "영조 (Yeongjo)", "정조 (Jeongjo)", "순조 (Sunjo)", "헌종 (Heonjong)", "철종 (Cheoljong)",
    "고종 (Gojong)", "순종 (Sunjong)"
]

REIGN_TK = {v[0]: v[3] for v in REIGN_INFO.values()}
REIGN_SPAN = {v[0]: (v[1], v[2]) for v in REIGN_INFO.values()}

# 1. 60명 코호트 구성 (상위 57명 + 4대 사례 중 나머지 3명: 정몽주, 민무구, 정도전)
top60_raw = []
with open("rev_top60.csv", "r", encoding="utf-8-sig") as f:
    top60_raw = list(csv.DictReader(f))

cases4_raw = []
with open("rev_4cases.csv", "r", encoding="utf-8-sig") as f:
    cases4_raw = list(csv.DictReader(f))

cohort_ids = set()
cohort = []
# 먼저 4대 사례 인물 포함 (신숙주, 정몽주, 민무구, 정도전)
for r in cases4_raw:
    cohort.append(r)
    cohort_ids.add(r["인물아이디"])

# 나머지 순위순으로 채워 정확히 60명 구성
for r in top60_raw:
    if len(cohort) >= 60:
        break
    if r["인물아이디"] not in cohort_ids:
        cohort.append(r)
        cohort_ids.add(r["인물아이디"])

cohort.sort(key=lambda x: int(x["total_mentions"]), reverse=True)
print(f"최종 분석 코호트 인원수: {len(cohort)}명")

# 2. 각 인물의 왕대별 언급 및 6차원 지표 계산
reign_cols = [c for c in cohort[0].keys() if c.startswith("w")]
reign_cohort_totals = {r: 0 for r in REIGN_ORDER}

records = []
for r in cohort:
    reign_cnt = {rn: 0 for rn in REIGN_ORDER}
    for c in reign_cols:
        code = c.split("_")[0]
        if code in REIGN_INFO:
            rn = REIGN_INFO[code][0]
            val = int(r[c])
            reign_cnt[rn] += val
            reign_cohort_totals[rn] += val

    # 가장 많이 언급된 주 활동 왕대(Peak Reign) 기준 partial 지표 산출
    peak_reign = max(REIGN_ORDER, key=lambda rn: reign_cnt[rn])
    Fp = reign_cnt[peak_reign]
    Tk = REIGN_TK[peak_reign]
    r_start, r_end = REIGN_SPAN[peak_reign]

    # 생몰년 기반 활동 기간(Ap) 및 생애 수명(Aa) 추정
    try:
        by = int(float(r["생년"]))
    except:
        by = r_start - 30
    try:
        dy = int(float(r["몰년"]))
    except:
        dy = r_end

    Aa = max(1, dy - by)
    # 해당 왕대 재위 기간 내 생존/활동 연수 Ap (최소 1년 ~ 최대 Tk)
    act_start = max(r_start, by + 20)
    act_end = min(r_end, dy)
    if act_end >= act_start:
        Ap = max(1, min(Tk, act_end - act_start + 1))
    else:
        # 사후 언급이 피크인 경우(예: 정몽주) 해당 왕대 내 집중 기록 연수(1년 단위)
        Ap = 1

    alpha = Ap / Tk
    Dp = Fp / Ap
    Fa = int(r["total_mentions"])
    Da = Fa / max(1, Aa)

    records.append({
        "인물아이디": r["인물아이디"],
        "한글_명": r["한글_명"],
        "한자_명": r["한자_명"],
        "생년": r["생년"],
        "몰년": r["몰년"],
        "관직": r["관직"],
        "peak_reign": peak_reign,
        "Tk": Tk,
        "Ap": Ap,
        "alpha": alpha,
        "Fp": Fp,
        "Dp": Dp,
        "Fa": Fa,
        "Aa": Aa,
        "Da": Da,
    })

# Min-Max 정규화 (수식 3, 4)
def minmax(vals):
    mn, mx = min(vals), max(vals)
    return [(v - mn) / (mx - mn) if mx > mn else 0.0 for v in vals]

Fp_star = minmax([x["Fp"] for x in records])
Ip_star = minmax([x["Dp"] for x in records])
Fa_star = minmax([x["Fa"] for x in records])
Ia_star = minmax([x["Da"] for x in records])
Aa_star = minmax([x["Aa"] for x in records])

for i, x in enumerate(records):
    x["Fp*"] = round(Fp_star[i], 4)
    x["Ip*"] = round(Ip_star[i], 4)
    x["Fa*"] = round(Fa_star[i], 4)
    x["Ia*"] = round(Ia_star[i], 4)
    x["Aa*"] = round(Aa_star[i], 4)
    x["alpha"] = round(x["alpha"], 4)

# 3. MECE 우선순위 규칙 기반 아키타입 분류 함수
def classify_mece(x, th_high=0.70, th_med=0.40, th_low=0.20):
    # Priority 1: Quadrant II (Crisis Catalysts / Posthumous Symbols)
    if x["Ip*"] >= th_high and x["alpha"] <= th_low:
        return "Quadrant II (Crisis Catalyst)"
    # Priority 2: Quadrant III (Sustained Dynastic Hegemons)
    elif x["Fa*"] >= th_high and x["Ia*"] >= th_med:
        return "Quadrant III (Sustained Hegemon)"
    # Priority 3: Quadrant I (Epochal Regime Architects)
    elif x["Ip*"] >= th_high and x["alpha"] >= th_med:
        return "Quadrant I (Regime Architect)"
    # Priority 4: Quadrant IV (Institutional Functionaries & Peripherals)
    else:
        return "Quadrant IV (Functionary/Peripheral)"

for x in records:
    x["Archetype"] = classify_mece(x)

# 4. 결과 출력: 아키타입별 정수 인원수 및 민감도 분석
from collections import Counter
dist = Counter(x["Archetype"] for x in records)
print("\n=== [1-2] MECE 4대 아키타입 정수 인원수 분포 (기준: 0.70 / 0.40 / 0.20) ===")
for k in sorted(dist.keys()):
    print(f"  - {k}: {dist[k]}명 ({dist[k]/60*100:.1f}%)")

print("\n=== 4대 사례 인물 실제 6차원 벡터 및 분류 결과 ===")
for x in records:
    if x["한글_명"] in ("정도전", "정몽주", "신숙주", "민무구"):
        print(f"  - {x['한글_명']} ({x['peak_reign']}): Fp*={x['Fp*']}, Ip*={x['Ip*']}, Ia*={x['Ia*']}, Fa*={x['Fa*']}, Aa*={x['Aa*']}, alpha={x['alpha']} -> {x['Archetype']}")

# 민감도 분석 (임계값 +-0.05 변화 시 분류 유지율)
print("\n=== [1-3] 임계값 민감도 분석 (Sensitivity Analysis) ===")
scenarios = [
    ("Baseline (0.70 / 0.40 / 0.20)", 0.70, 0.40, 0.20),
    ("Strict (-0.05 -> 0.75 / 0.45 / 0.15)", 0.75, 0.45, 0.15),
    ("Relaxed (+0.05 -> 0.65 / 0.35 / 0.25)", 0.65, 0.35, 0.25),
]
base_labels = [classify_mece(x, 0.70, 0.40, 0.20) for x in records]
for label, h, m, l in scenarios:
    cur_labels = [classify_mece(x, h, m, l) for x in records]
    same = sum(1 for a, b in zip(base_labels, cur_labels) if a == b)
    c = Counter(cur_labels)
    print(f"  * {label}: 일치율 {same}/60 ({same/60*100:.1f}%) | Q1={c['Quadrant I (Regime Architect)']}, Q2={c['Quadrant II (Crisis Catalyst)']}, Q3={c['Quadrant III (Sustained Hegemon)']}, Q4={c['Quadrant IV (Functionary/Peripheral)']}")

# 5. 왕대별 60명 코호트 언급 총합 및 재위 연수(Tk) 정규화 빈도 저장
with open("rev_cohort60_metrics.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    w.writeheader()
    w.writerows(records)

with open("rev_reign_normalized.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["reign", "reign_years_Tk", "cohort60_mentions", "mentions_per_reign_year"])
    for rn in REIGN_ORDER:
        tot = reign_cohort_totals[rn]
        tk = REIGN_TK[rn]
        w.writerow([rn, tk, tot, round(tot / tk, 2)])

print("\n저장 완료: rev_cohort60_metrics.csv, rev_reign_normalized.csv")