import os
import json
from engine.constants import BASE_PATH

# 사용자 수강 이력 불러오기
def load_student_data(user_id: str) -> list:
    name_map = {
        "kim": "김브티",
        "hong": "홍데사"
    }
    filename = f"{name_map.get(user_id, user_id)}_수강이력.json"
    path = os.path.join(BASE_PATH, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# 시나리오 질문-응답 세트 불러오기
def load_scenario_data() -> list:
    files = ["학습현황.json", "강의탐색.json", "진로상담.json"]
    all_data = []
    for fname in files:
        path = os.path.join(BASE_PATH, fname)
        try:
            with open(path, encoding="utf-8") as f:
                all_data.extend(json.load(f))
        except FileNotFoundError:
            print(f"⚠️ 시나리오 파일 누락: {path}")
    return all_data
