import csv

# 1. 인물 부가정보 로드
person_meta = {}
with open("교육부 국사편찬위원회_조선왕조실록 정보_실록부가정보_인물.csv", "r", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        pid = row.get("인물아이디", "").strip()
        if pid:
            person_meta[pid] = row

# 2. 전체 언급 집계 파일 로드 및 한국사 인물 필터링
kr_rows = []
kr_with_bio_count = 0
bio_cols = ['생년', '몰년', '관직', '한글_시호', '한글_호', '한글_묘호', '한글_자', '한글_본관']

with open("all_persons_mentions.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    orig_fields = reader.fieldnames
    for row in reader:
        pid = row["인물아이디"]
        m = person_meta.get(pid, {})
        nation = m.get("국가", "").strip()
        # 제순, 제요, 주희, 공자 등 외국/고대중국 인물 제외
        if nation == "" or nation == "고려(高麗)":
            row["국가"] = nation
            row["한글_자"] = m.get("한글_자", "")
            row["한글_본관"] = m.get("한글_본관", "")
            kr_rows.append(row)
            if any(m.get(c, "").strip() not in ("", "?", "9999") for c in bio_cols):
                kr_with_bio_count += 1

print(f"한국사 전체 언급 인물: {len(kr_rows):,}명 / 인적 메타데이터 보유 인물: {kr_with_bio_count:,}명")

# 3. 4대 사례 인물 실제 수치 확인
target_ids = {"M_0005761", "M_0005774", "M_0003129", "M_0002306"}  # 정도전, 정몽주, 신숙주, 민무구
case_rows = []
print("\n=== 4대 사례 인물 실제 전수 데이터 ===")
for idx, row in enumerate(kr_rows, 1):
    row["kr_rank"] = idx
    if row["인물아이디"] in target_ids:
        case_rows.append(row)
        print(f"순위 {idx:,}위 | {row['인물아이디']} | {row['한글_명']} ({row['한자_명']}) | 총언급={row['total_mentions']}회 | 생몰={row['생년']}~{row['몰년']} | 관직={row['관직']}")

# 4. 결과 CSV 저장
out_fields = ["kr_rank"] + orig_fields + ["국가", "한글_자", "한글_본관"]

with open("rev_top60.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out_fields)
    w.writeheader()
    w.writerows(kr_rows[:60])

with open("rev_4cases.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out_fields)
    w.writeheader()
    w.writerows(case_rows)

print("\n저장 완료: rev_top60.csv, rev_4cases.csv")