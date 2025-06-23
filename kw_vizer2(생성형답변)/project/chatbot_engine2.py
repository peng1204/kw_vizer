from retrieval2 import (
    get_retrieval_qa,
    get_vectorstore,
    match_scenario_answer,
    find_best_matching_answer
)
from embedding2 import ko_embedding
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# ✅ 기능별 프롬프트
PROMPT_MAP = {
    "lecture": PromptTemplate(
        input_variables=["context", "question"],
        template="""
        가능한 한 임베딩된 전체 문서에서 강의 추천 정보를 탐색하세요.
        교수님 이름이 명확하게 일치하는 경우, 해당 교수님의 강의를 추천하세요.
        특히 "lecture_professor", "강의 계획", "평점", "커리큘럼" 등 다양한 항목을 종합해서 응답해 주세요.

        📄 문서: {context}
        💬 질문: {question}
        """
    ),
    "status": PromptTemplate(
        input_variables=["context", "question"],
        template="""
        성적 표현은 반드시 데이터에 있는 A+, A0, B+, B0 등으로만 응답하세요.
        졸업 요건은 2022학번 기준 133학점입니다.
        평균값 유추 금지.

        📄 문서: {context}
        💬 질문: {question}
        """
    ),
    "review": PromptTemplate(
        input_variables=["context", "question"],
        template="""
        조별과제 여부, 시험 난이도 관련 질문은 반드시 "강의 평점.json"만 사용해서 응답하세요.
        문서에 없는 내용은 "정보가 제공되지 않았습니다"라고 답변하세요.

        📄 문서: {context}
        💬 질문: {question}
        """
    ),
    "career": PromptTemplate(
        input_variables=["context", "question"],
        template="""
        진로 관련 답변은 반드시 수강 이력, 성적, 이수 과목 데이터를 기반으로만 응답하세요.
        일반화하거나 유추하지 마세요.

        📄 문서: {context}
        💬 질문: {question}
        """
    ),
    "general": PromptTemplate(
        input_variables=["context", "question"],
        template="""
        📄 문서: {context}
        💬 질문: {question}
        """
    )
}

# ✅ LLM 설정
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o",
    openai_api_key="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"
)

# ✅ 핵심 응답 함수
def answer_query(user_id: str, user_input: str, collection_name: str) -> str:
    print(f"=== 🧠 answer_query 진입 (user_id: {user_id}) ===")
    print(f"📦 선택된 컬렉션 이름: {collection_name}")

    # 1. 시나리오 기반 매칭
    matched_answer = match_scenario_answer(user_input)
    if matched_answer:
        print("✅ 시나리오 매칭 성공")
        return matched_answer

    # 2. 기능 추론 (기능별 프롬프트 선택)
    task_type = "lecture" if "강의" in user_input else (
        "status" if "학점" in user_input or "졸업" in user_input else (
            "review" if "조별" in user_input or "시험" in user_input else (
                "career" if "진로" in user_input else "general"
            )
        )
    )
    prompt = PROMPT_MAP[task_type]

    # 3. RetrievalQA 기반 생성형 응답
    try:
        qa = get_retrieval_qa(llm=llm, prompt=prompt, collection_name=collection_name)
        result = qa.invoke({"query": user_input})
        print("🧠 생성형 응답 성공")
        return result.get("result", "응답 생성 실패")
    except Exception as e:
        print(f"❌ 생성형 응답 실패: {e}")

    # 4. fallback: 전공 기반 시나리오 유사도
    fallback = find_best_matching_answer(user_input, user_id)
    print("🔁 fallback 응답 반환")
    return fallback

# ✅ 내보내기
__all__ = ["answer_query"]