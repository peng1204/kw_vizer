import json
import re

# JSON 파일 경로
JSON_PATH = "json/kw_chatbot_data - 홍데사_성적.json"

# JSON 데이터 로드
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"✅ 성적 데이터 불러오기 완료! 총 항목 수: {len(data)}개")

# 질문에 따른 응답 처리
def answer_query(data, question):
    q = question.lower()
    results = []

    if "신청학점" in q:
        entry = next((d for d in data if d["category"] == "신청학점"), None)
        if entry:
            if "전공" in q:
                results.append(f"✅ 신청학점 - 전공: {entry.get('전공', '정보 없음')}학점")
            elif "교양" in q:
                results.append(f"✅ 신청학점 - 교양: {entry.get('교양', '정보 없음')}학점")
            else:
                results.append(f"✅ 신청학점 총계: {entry.get('계', '정보 없음')}학점")
    
    elif "삭제학점" in q:
        entry = next((d for d in data if d["category"] == "삭제학점"), None)
        if entry:
            if "전공" in q:
                results.append(f"✅ 삭제학점 - 전공: {entry.get('전공', '정보 없음')}학점")
            elif "교양" in q:
                results.append(f"✅ 삭제학점 - 교양: {entry.get('교양', '정보 없음')}학점")
            else:
                results.append("✅ 삭제학점은 모두 0학점입니다.")

    elif "취득학점" in q:
        entry = next((d for d in data if d["category"] == "취득학점"), None)
        if entry:
            if "전공" in q:
                results.append(f"✅ 취득학점 - 전공: {entry.get('전공', '정보 없음')}학점")
            elif "교양" in q:
                results.append(f"✅ 취득학점 - 교양: {entry.get('교양', '정보 없음')}학점")
            else:
                results.append(f"✅ 취득학점 총계: {entry.get('계', '정보 없음')}학점")
    
    elif "평량평균" in q or "총학점" in q:
        entry = next((d for d in data if d["category"].startswith("평량평균")), None)
        if entry:
            results.append(f"✅ 평량평균은 {entry.get('계', '정보 없음')}입니다.")
    
    else:
        results.append("🤖 아직 지원하지 않는 질문이에요.")
    
    return results

# 여러 문장 한 번에 처리하는 함수
def run_flexible_queries(data, raw_input):
    print("\n📌 검색 결과:")
    questions = re.split(r'[?？\n]', raw_input)
    questions = [q.strip() + '?' for q in questions if q.strip()]

    for q in questions:
        print(f"\n❓ {q}")
        for res in answer_query(data, q):
            print(res)

# 테스트 실행
if __name__ == "__main__":
    input_text = """
    신청학점이 얼마야?
    신청학점 전공은?
    신청학점 교양은?
    삭제학점이 얼마야?
    삭제학점 전공은?
    삭제학점 교양은?
    취득학점이 얼마야?
    취득학점 전공은?
    취득학점 교양은?
    총학점이 얼마야?
    평량평균이 얼마야?
    """

    run_flexible_queries(data, input_text)
