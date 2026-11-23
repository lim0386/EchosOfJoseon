import os
import glob
import csv
import random
import xml.etree.ElementTree as ET

random.seed(2026)

# 1. 인물 메타데이터 로드
person_meta = {}
with open("교육부 국사편찬위원회_조선왕조실록 정보_실록부가정보_인물.csv", "r", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        pid = row.get("인물아이디", "").strip()
        if pid:
            person_meta[pid] = row

# 2. 전체 XML에서 type="이름" 및 ref 보유 태그 수집
xml_files = sorted(glob.glob(os.path.join(".", "**", "*.xml"), recursive=True))
candidates = []

for fp in xml_files:
    try:
        root = ET.parse(fp).getroot()
    except Exception:
        continue
    title_el = root.find("./front/biblioData/title/mainTitle")
    reign_title = (title_el.text or "").strip() if title_el is not None else ""
    for lvl3 in root.findall(".//level3"):
        art_id = lvl3.attrib.get("id", "")
        full_para = "".join(lvl3.itertext()).strip().replace("\n", " ")
        for idx_el in lvl3.findall(".//index"):
            if idx_el.attrib.get("type") == "이름":
                ref = idx_el.attrib.get("ref", "").strip()
                surface = (idx_el.text or "").strip()
                if ref:
                    m = person_meta.get(ref, {})
                    candidates.append({
                        "file": os.path.basename(fp),
                        "reign_title": reign_title,
                        "article_id": art_id,
                        "ref_id": ref,
                        "mapped_name_kr": m.get("한글_명", ""),
                        "mapped_name_hj": m.get("한자_명", ""),
                        "surface_text": surface,
                        "context_snippet": full_para[:220],
                        "is_tp_manual": "",   # 1: 정분류(TP), 0: 오분류(FP) 직접 기입
                        "missed_fn_count": 0 # 해당 문맥 내 누락된 인명 수(FN) 직접 기입
                    })

sample_100 = random.sample(candidates, min(100, len(candidates)))
with open("audit_100_samples.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=list(sample_100[0].keys()))
    writer.writeheader()
    writer.writerows(sample_100)

print(f"총 후보 {len(candidates):,}건 중 무작위 표본 {len(sample_100)}건 저장 완료: audit_100_samples.csv")