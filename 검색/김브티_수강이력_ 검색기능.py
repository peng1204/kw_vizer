import chromadb
import json
import re

# 1. ChromaDB 서버 연결
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

# 2. 저장했던 collection 열기
collection = chroma_client.get_collection(name="vt_course_history")

# 3. 성적 → 평점 매핑
grade_to_score = {
    "A+": 4.5, "A0": 4.0,
    "B+": 3.5, "B0": 3.0,
    "C+": 2.5, "C0": 2.0,
    "D+": 1.5, "D0": 1.0,
    "F": 0.0
}

# 4. 질문에 따른 응답 처리
def answer_query(question):
    q = question.lower()
    q_nospace = q.replace(" ", "")
    results = []

    # 🔍 ChromaDB에서 전체 데이터 가져오기
    all_data = collection.get(include=["documents"])
    docs = [json.loads(doc) for doc in all_data["documents"] if doc is not None]

    # 전선 평균
    if ("전선" in q and "평균" in q) or "전선성적평균" in q_nospace or "전선평균" in q_nospace:
        scores = [grade_to_score.get(d.get("grade", "F"), 0) for d in docs if d.get("course_type") == "전선"]
        avg = sum(scores) / len(scores) if scores else 0
        results.append(f"📊 전선 과목 평점 평균은 {avg:.2f}입니다.")

    # 전체 평균
    elif "평균" in q:
        scores = [grade_to_score.get(d.get("grade", "F"), 0) for d in docs]
        avg = sum(scores) / len(scores) if scores else 0
        results.append(f"📊 전체 성적 평점 평균은 {avg:.2f}입니다.")

    elif "전선" in q and "몇 개" in q:
        count = sum(1 for d in docs if d.get("course_type") == "전선")
        results.append(f"✅ 전선 과목은 총 {count}개입니다.")

    elif "전선" in q and ("뭐가 있어" in q or "과목" in q):
        subjects = [d.get("lecture_name") for d in docs if d.get("course_type") == "전선"]
        results.append(f"✅ 전선 과목 목록: {', '.join(subjects)}")

    elif "성적" in q:
        for d in docs:
            if d.get("lecture_name") and d["lecture_name"] in question:
                results.append(f"✅ {d['lecture_name']} 성적은 {d['grade']}입니다.")
                break

    elif "전선이지" in q or "전선이야" in q:
        for d in docs:
            if d.get("lecture_name") and d["lecture_name"] in question:
                ct = d.get("course_type", "")
                msg = "✅ 전선 과목입니다." if ct == "전선" else f"✅ {ct} 과목입니다."
                results.append(f"{d['lecture_name']}은 {msg}")
                break

    elif "c+" in q:
        subjects = [d.get("lecture_name") for d in docs if d.get("grade", "").upper() == "C+"]
        results.append(f"✅ C+ 받은 과목: {', '.join(subjects)}")

    elif "f 받은" in q:
        subjects = [d.get("lecture_name") for d in docs if d.get("grade", "").upper() == "F"]
        results.append("✅ F 받은 과목은 없습니다." if not subjects else f"❌ F 받은 과목: {', '.join(subjects)}")

    elif "b 이상" in q:
        subjects = [d.get("lecture_name") for d in docs if grade_to_score.get(d.get("grade", "F"), 0) >= 3.0]
        results.append(f"✅ B0 이상 성적 받은 과목: {', '.join(subjects)}")

    else:
        results.append("🤖 아직 지원하지 않는 질문이에요.")

    return results

# 5. 여러 문장 한 번에 처리
def run_flexible_queries(raw_input):
    print("\n📌 결과:")
    questions = re.split(r'[?？\n]', raw_input)
    questions = [q.strip() + '?' for q in questions if q.strip()]

    for q in questions:
        print(f"\n❓ {q}")
        for res in answer_query(q):
            print(res)

# 6. 테스트 실행
if __name__ == "__main__":
    input_text = """
    전체 성적 평균이 어떻게 돼?
    전선 성적 평균은?
    평균 알려줘
    그래픽디자인 성적이 뭐더라?
    객체지향프로그래밍 성적이 뭐야?
    객체지향프로그래밍은 전선이지?
    F 받은 과목은?
    B 이상 받은 과목은?
    내가 C+ 받은 과목은 뭐가 있어?
    """

    run_flexible_queries(input_text)
