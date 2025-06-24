from difflib import SequenceMatcher
from engine.data_loader import load_scenario_data

SCENARIOS = load_scenario_data()

# 시나리오 질문과 가장 유사한 항목 찾기
def match_scenario_answer(user_input: str, threshold: float = 0.83) -> str | None:
    norm_input = user_input.replace(" ", "").lower()
    best_score = 0
    best_answer = None

    for item in SCENARIOS:
        q = item.get("Text", "").replace(" ", "").lower()
        a = item.get("Completion", "")
        score = SequenceMatcher(None, norm_input, q).ratio()
        if score > best_score:
            best_score = score
            best_answer = a

    return best_answer if best_score >= threshold else None
