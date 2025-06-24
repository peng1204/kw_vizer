from engine.constants import GRADE_TO_POINT, USER_NAME
from engine.data_loader import load_student_data

def handle_gpa_queries(user_input: str, user_id: str) -> str | None:
    normalized = user_input.replace(" ", "").lower()

    if "전체성적평균" in normalized or "전체학점평균" in normalized:
        gpa = calculate_gpa(user_id)
        if gpa is not None:
            name = USER_NAME.get(user_id, user_id)
            return f"{name}님의 전체 성적 평균은 {gpa:.2f}입니다."

    if "전공" in normalized and "평균" in normalized:
        gpa = calculate_gpa(user_id, course_type="전공")
        if gpa is not None:
            name = USER_NAME.get(user_id, user_id)
            return f"{name}님의 전공 성적 평균은 {gpa:.2f}입니다."

    return None

def calculate_gpa(user_id: str, course_type: str = None) -> float | None:
    data = load_student_data(user_id)
    total_points, total_credits = 0, 0

    for record in data:
        if record.get("retake_or_delete_status") == "Y":
            continue

        grade = record.get("lecutre_grade")
        point = GRADE_TO_POINT.get(grade)
        credit = record.get("lecture_credit", 0)
        ctype = record.get("lecture_course_type", '')

        if course_type == "전공" and not ctype.startswith("전"):
            continue

        if point is None or not isinstance(credit, (int, float)):
            continue

        total_points += point * credit
        total_credits += credit

    if total_credits == 0:
        return None

    return total_points / total_credits
