##함수

import json
import re
import random

def filter_lectures_by_team(json_files, team_condition):
    result = []
    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            team_value = item.get("lecture_team", "").strip()
            lecture_id = item.get("lecture_id")
            lecture_name = item.get("lecture_name")

            if not lecture_id or not lecture_name:
                continue

            if team_condition == "없음" and team_value in ["없음", "0"]:
                result.append({"lecture_id": lecture_id, "lecture_name": lecture_name})
            elif team_condition == "보통" and team_value == "보통":
                result.append({"lecture_id": lecture_id, "lecture_name": lecture_name})
            elif team_condition == "많은" and team_value == "많음":
                result.append({"lecture_id": lecture_id, "lecture_name": lecture_name})
    return result

