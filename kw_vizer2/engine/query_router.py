from engine.retrieval import get_llm_response
from engine.rules import handle_fixed_responses
from engine.gpa_utils import handle_gpa_queries
from engine.scenario_matcher import match_scenario_answer
from engine.constants import USER_NAME

def answer_query(user_input: str, user_id: str = "kim") -> str:
    normalized = user_input.replace(" ", "").lower()

    # 1. 고정 응답 우선 처리 (졸업, 재수강 등)
    fixed = handle_fixed_responses(user_input, user_id)
    if fixed:
        return fixed

    # 2. GPA, 성적 관련 처리
    gpa_response = handle_gpa_queries(user_input, user_id)
    if gpa_response:
        return gpa_response

    # 3. 시나리오 기반 응답
    scenario = match_scenario_answer(user_input)
    if scenario:
        return scenario

    # 4. 벡터 검색 + LLM 응답
    return get_llm_response(user_input)

    # 5. fallback
    return "죄송합니다. 적절한 답변을 찾을 수 없습니다."