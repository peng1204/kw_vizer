from langchain.prompts import PromptTemplate

# ✅ Lecture Recommendation Prompt
lecture_prompt = PromptTemplate.from_template("""
❗ 반드시 아래 문서 내 정보만 사용해서 답변하세요.
❌ 문서에 없는 정보는 생성하지 마세요.
❌ 유추, 추론, 보완, 일반 상식 사용 금지.

- 두 개 이상인 경우에는 **모두 나열**하세요.
- 조건에 맞는 강의가 없는 경우, "추천할 수 있는 과목이 없습니다."라고 하세요.
- "수강이력.json"에 있는 과목은 제외하고 추천하세요.
- 000교수님 강의 추천해줘 → 질문에는 "수강신청자료집.json"에서 lecture_professor 항목에서 검색하여 대답하세요.
- 반드시 "수강신청 자료집.json"과 "수강신청_자료집_전체.pdf" 파일만 사용하세요.
- 교수님 이름을 헷갈리지 말고 정확히 적어주세요.
- 예: "OOO 교수님 강의 추천해줘" → "OOO 교수님의 강의 OOO 추천 드립니다."

📄 문서: {context}
💬 질문: {question}
""")

# ✅ Academic Status Prompt
status_prompt = PromptTemplate.from_template("""
📌 질문 유형: 학습현황, 성적

- 성적 표현은 반드시 데이터에 있는 A+, A0, B+, B0, C+, C0, F 등등으로만 응답하세요.
- 유사 성적 포함, 평균값 추론은 절대 하지 마세요.
- 졸업 학점 기준은 "2022학년도 입학자" 기준으로 133학점 입니다. 이에 맞춰 졸업 가능 여부를 판단하세요.
- 전체 성적 평균, 이수 학점 등은 반드시 데이터 기반으로만 응답하세요.

📄 문서: {context}
💬 질문: {question}
""")

# ✅ Lecture Review Prompt
review_prompt = PromptTemplate.from_template("""
📌 질문 유형: 강의평가

- 조별과제, 팀플 여부, 시험 성적 너그러움 여부에 대한 질문은 반드시 "강의 평점.json" 파일만 사용해서 답하세요.
- "빡세다", "쉽다" 같은 평가는 문서에 있는 평가만 근거로 응답하세요.

📄 문서: {context}
💬 질문: {question}
""")

# ✅ Career Counseling Prompt
career_prompt = PromptTemplate.from_template("""
📌 질문 유형: 진로상담

- 사용자의 전공, 성적, 이수 과목 등을 기반으로 진로 방향을 추천하세요.
- 현실적인 취업 정보, 직무 설명 등은 반드시 문서 기반 정보로 제한하세요.
- 없는 경우 "해당 직무에 대한 정보가 제공되지 않았습니다."라고 하세요.

📄 문서: {context}
💬 질문: {question}
""")

# ✅ 기본 프롬프트 (fallback)
default_prompt = PromptTemplate.from_template("사용자 질문: {question}\n답변:")

# ✅ 프롬프트 매핑
PROMPT_MAP = {
    "lecture": lecture_prompt,
    "status": status_prompt,
    "review": review_prompt,
    "career": career_prompt,
    "general": default_prompt
}  # fallback 용도 포함
