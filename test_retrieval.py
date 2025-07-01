import re
import random
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTORSTORE_PATH = "./data/chroma_db"
SUMMARY_COLLECTION = "lecture_flat"

ko_embedding = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask", 
    model_kwargs={"device": "cpu"}
)

def parse_lecture_fields(text):
    # 예시: "강의명: 자료구조 / 교수명: 박규동 / 이수구분: 전선 / ..."
    fields = {}
    for part in re.split(r"\s*/\s*", text):
        if ":" in part:
            key, val = part.split(":", 1)
            fields[key.strip()] = val.strip()
    return fields

def normalize_professor_name(name):
    return name.replace("교수님", "").replace("교수", "").strip()

def parse_times(raw_time):
    # "화3,목4" -> ["화3", "목4"]
    if not raw_time:
        return []
    return [x for x in re.split(r'[,\s/]+', raw_time) if x and re.match(r'^(월|화|수|목|금|토)\d+$', x)]

def filter_summary_docs_by_query(summary_docs, query, k=3):
    # 쿼리 파싱
    time_pat = re.findall(r'(월|화|수|목|금|토)\d+', query.replace(" ", ""))
    day_pat = re.findall(r'(월|화|수|목|금|토)요일', query)
    prof_pat = re.findall(r'([가-힣]{2,}) ?교수(님)?', query)
    course_pat = re.findall(r'(전선|전필|교선|교필|교양|전공)', query)
    k_pat = re.search(r'(\d+)\s*개', query)
    if k_pat:
        k = int(k_pat.group(1))

    results = []
    for doc, score in summary_docs:
        fields = parse_lecture_fields(doc.page_content)
        matched = True

        # 시간 완전 일치
        if time_pat:
            lecture_times = parse_times(fields.get("강의시간", ""))
            if not all(tp in lecture_times for tp in time_pat):
                matched = False
        # 요일 포함(요일만 있는 경우)
        if day_pat:
            lecture_times = parse_times(fields.get("강의시간", ""))
            if not any(t.startswith(day_pat[0]) for t in lecture_times):
                matched = False
        # 교수명 일치
        if prof_pat:
            query_profs = [normalize_professor_name(p[0]) for p in prof_pat]
            lec_prof = normalize_professor_name(fields.get("교수명", ""))
            if not any(qp == lec_prof for qp in query_profs):
                matched = False
        # 이수구분(전선, 교선 등) 일치
        if course_pat:
            lec_type = fields.get("이수구분", "")
            if not any(ct in lec_type for ct in course_pat):
                matched = False
        if matched:
            results.append(fields)
    # 랜덤 추출
    if len(results) > k:
        results = random.sample(results, k)
    return results

def get_lecture_recommendations(query):
    # 벡터스토어 연결
    vs = Chroma(
        persist_directory=VECTORSTORE_PATH,
        collection_name=SUMMARY_COLLECTION,
        embedding_function=ko_embedding
    )
    # 일단 상위 100개 정도만 뽑고, 쿼리조건으로 다시 필터
    summary_docs = vs.similarity_search_with_score(query, k=100)
    results = filter_summary_docs_by_query(summary_docs, query)
    if not results:
        return "추천할 수 있는 강의가 없습니다."
    # 결과 포맷: 챗봇 자연어 응답으로 묶어주기
    msg = "\n".join(
        f"{i+1}. {r['강의명']} (교수: {r.get('교수명', '-')}, 이수구분: {r.get('이수구분', '-')}, 시간: {r.get('강의시간', '-')})"
        for i, r in enumerate(results)
    )
    return msg

# ===================== 테스트 ========================

if __name__ == "__main__":
    queries = [
        "금요일 교선 3개만 추천해줘",    # 특정요일+이수구분
        "화3 교선 추천해줘",         # 시간+이수구분
        "화요일 전선 3개만 추천해줘",    # 요일+이수구분
        "박규동교수님 전선 수업 추천 좀",  # 교수+이수구분
        "이혜정 교수님 교선 추천해줘"      # 교수+이수구분
    ]
    for q in queries:
        print(f"\n[질문] {q}")
        print(get_lecture_recommendations(q))
