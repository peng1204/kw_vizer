def handle_fixed_responses(user_input: str, user_id: str) -> str | None:
    lowered = user_input.lower()
    normalized = lowered.replace(" ", "")

    # 졸업논문/졸업프로젝트 관련
    if all(k in lowered for k in ["졸업", "논문", "프로젝트"]) and any(w in lowered for w in ["언제", "시기", "몇학년", "준비"]):
        return "빠르면 3학년부터 준비하는 경우도 있지만, 대부분 3학년 2학기부터 팀을 구한 후 4학년에 진행합니다."

    if all(k in lowered for k in ["졸업", "논문", "프로젝트"]) and any(w in lowered for w in ["필수", "의무", "꼭", "반드시"]):
        return "졸업을 위해 졸업 논문 혹은 졸업 프로젝트 중 하나는 필수입니다."

    if any(k in normalized for k in ["졸프", "졸작", "졸업과제"]):
        return "졸업 논문이나 프로젝트는 학과 졸업 요건에 따라 다르므로, 학과 사무실이나 지도 교수님께 문의하세요."

    # 고정 응답 예시 (필요시 계속 확장 가능)
    if "졸업유예" in normalized:
        return "우리 학교에서는 졸업 유예 신청이 불가능합니다."

    if "f받고재수강" in normalized or ("f" in normalized and "재수강" in normalized):
        return "F 받은 과목은 재수강 시 '재수강' 표시가 뜨지 않지만, 성적표에는 'R'로 표기됩니다."

    if "동일과목" in normalized and "몇번" in normalized:
        return "C+ 이하인 동일과목은 최대 2회까지 재수강 가능하며, 전체 재수강은 최대 8과목입니다."

    if "휴학" in normalized and "몇번" in normalized:
        return "일반휴학은 최대 6학기 가능하며, 한 번에 최대 2학기까지 신청할 수 있습니다. 군휴학은 별도입니다."

    return None
