import os
import glob
import csv
import xml.etree.ElementTree as ET
from collections import defaultdict

# 1. XML 파일들이 들어있는 폴더 경로 (현재 폴더에 두면 "." 그대로 사용)
XML_DIR = r"."  # 필요시 r"C:\Users\...\교육부 국사편찬위원회_조선왕조실록 정보_실록원문" 로 수정

# 2. 아까 받으신 인물 CSV 파일 경로
PERSON_CSV = r"교육부 국사편찬위원회_조선왕조실록 정보_실록부가정보_인물.csv"

def load_person_meta(csv_path):
    meta = {}
    if not os.path.exists(csv_path):
        print(f"[주의] {csv_path} 파일을 찾지 못해 ID 기준으로만 집계합니다.")
        return meta
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get("인물아이디", "").strip()
            if pid:
                meta[pid] = row
    print(f"인물 메타데이터 로드 완료: {len(meta):,}명")
    return meta

def parse_all_xml(xml_dir):
    xml_files = sorted(glob.glob(os.path.join(xml_dir, "**", "*.xml"), recursive=True))
    print(f"총 XML 파일 수: {len(xml_files)}개")

    total_counts = defaultdict(int)
    reign_counts = defaultdict(lambda: defaultdict(int))
    reign_total_mentions = defaultdict(int)
    raw_surface_forms = defaultdict(set)
    unlinked_name_count = 0
    linked_name_count = 0

    for idx, filepath in enumerate(xml_files, 1):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except Exception as e:
            print(f"[오류] {filepath}: {e}")
            continue

        # 왕대 실록 제목 추출 (예: 太祖實錄)
        reign_title = "Unknown"
        title_el = root.find("./front/biblioData/title/mainTitle")
        if title_el is not None and title_el.text:
            reign_title = title_el.text.strip()
        reign_id = root.attrib.get("id", "unknown")
        reign_key = f"{reign_id}_{reign_title}"

        # 본문(level3) 내 인물 인덱스 태그 순회
        for index_el in root.findall(".//level3//index"):
            if index_el.attrib.get("type") == "이름":
                ref_id = index_el.attrib.get("ref", "").strip()
                surface = (index_el.text or "").strip()
                if ref_id:
                    linked_name_count += 1
                    total_counts[ref_id] += 1
                    reign_counts[ref_id][reign_key] += 1
                    reign_total_mentions[reign_key] += 1
                    if surface and len(raw_surface_forms[ref_id]) < 15:
                        raw_surface_forms[ref_id].add(surface)
                else:
                    unlinked_name_count += 1

        if idx % 100 == 0 or idx == len(xml_files):
            print(f"진행률: {idx}/{len(xml_files)} 파일 완료...")

    print(f"\n집계 완료! 고유 인물 ID 수: {len(total_counts):,}명")
    print(f"ID 연결된 인명 언급 총계: {linked_name_count:,}건 / ID 미연결(외국인·미상 등): {unlinked_name_count:,}건")
    return total_counts, reign_counts, reign_total_mentions, raw_surface_forms

def main():
    meta = load_person_meta(PERSON_CSV)
    total_counts, reign_counts, reign_total_mentions, raw_surface_forms = parse_all_xml(XML_DIR)

    # 정렬된 전체 왕대 키 목록
    all_reigns = sorted(reign_total_mentions.keys())

    # 1) 왕대별 전체 언급 요약 저장
    with open("reign_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["reign_key", "total_linked_mentions"])
        for rk in all_reigns:
            writer.writerow([rk, reign_total_mentions[rk]])

    # 2) 전체 인물 및 상위 100명 상세 저장
    sorted_persons = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)
    header = [
        "rank", "인물아이디", "한글_명", "한자_명", "생년", "몰년", "관직",
        "한글_시호", "한글_호", "한글_묘호", "total_mentions", "표기변형_예시"
    ] + all_reigns

    with open("all_persons_mentions.csv", "w", newline="", encoding="utf-8-sig") as f_all, \
         open("top100_persons_mentions.csv", "w", newline="", encoding="utf-8-sig") as f_top:
        w_all = csv.writer(f_all)
        w_top = csv.writer(f_top)
        w_all.writerow(header)
        w_top.writerow(header)

        for rank, (pid, cnt) in enumerate(sorted_persons, 1):
            m = meta.get(pid, {})
            row = [
                rank,
                pid,
                m.get("한글_명", ""),
                m.get("한자_명", ""),
                m.get("생년", ""),
                m.get("몰년", ""),
                m.get("관직", ""),
                m.get("한글_시호", ""),
                m.get("한글_호", ""),
                m.get("한글_묘호", ""),
                cnt,
                " | ".join(sorted(raw_surface_forms[pid]))
            ] + [reign_counts[pid].get(rk, 0) for rk in all_reigns]

            w_all.writerow(row)
            if rank <= 100:
                w_top.writerow(row)

    print("생성 완료: reign_summary.csv, top100_persons_mentions.csv, all_persons_mentions.csv")

if __name__ == "__main__":
    main()