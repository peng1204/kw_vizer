# ✅ 리팩토링된 retrieval2.py (임베딩 기반 시나리오 매칭)

import os
import json
from typing import Optional
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma  # ✅ 최신 권장 방식
from langchain_core.documents import Document
from embedding2 import ko_embedding, client, embeddings_model

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ✅ 벡터스토어 반환
def get_vectorstore(collection_name: str) -> Chroma:
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=ko_embedding
    )

# ✅ Retriever 객체 생성
def get_retriever(collection_name: str):
    return get_vectorstore(collection_name).as_retriever(search_kwargs={"k": 20})

# ✅ RetrievalQA 생성
def get_retrieval_qa(llm, prompt: PromptTemplate, collection_name: str) -> RetrievalQA:
    retriever = get_vectorstore(collection_name).as_retriever()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )

# ✅ 시나리오 데이터 불러오기
SCENARIO_PATHS = [
    "/Users/hyunjin/Desktop/학습현황2.json",
    "/Users/hyunjin/Desktop/강의탐색3.json",
    "/Users/hyunjin/Desktop/진로상담.json"
]

def load_scenario_data() -> list[dict]:
    data = []
    for path in SCENARIO_PATHS:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data.extend(json.load(f))
        else:
            print(f"⚠️ 시나리오 파일 없음: {path}")
    return data

SCENARIOS = load_scenario_data()

# ✅ 사용자 입력과 시나리오 문장을 임베딩 후 cosine similarity 비교
def match_scenario_answer(user_input: str, threshold: float = 0.83) -> Optional[str]:
    candidate_pairs = [(item.get("Text", ""), item.get("Completion", "")) for item in SCENARIOS]
    texts = [q for q, _ in candidate_pairs]

    if not texts:
        return None

    # 문장 임베딩
    embedded_candidates = embeddings_model.embed_documents(texts)
    embedded_input = embeddings_model.embed_query(user_input)

    sims = cosine_similarity([embedded_input], embedded_candidates)[0]
    best_idx = int(np.argmax(sims))
    best_score = sims[best_idx]

    if best_score >= threshold:
        return candidate_pairs[best_idx][1]
    return None

# ✅ fallback: 세부전공 기반 유사도 답변 (기존 SequenceMatcher 유지)
def find_best_matching_answer(user_input: str, user_id: str) -> str:
    from difflib import SequenceMatcher
    major = "VT" if user_id == "kim" else "DS"
    major_data = [item for item in SCENARIOS if item.get("세부전공") == major]

    norm_input = user_input.replace(" ", "").lower()
    best_score = 0
    best_answer = None

    for item in major_data or SCENARIOS:
        q = item.get("Text", "")
        a = item.get("Completion", "")
        q_norm = q.replace(" ", "").lower()
        score = SequenceMatcher(None, norm_input, q_norm).ratio()
        if score > best_score:
            best_score = score
            best_answer = a

    return best_answer or "해당 질문에 대한 적절한 답변을 찾을 수 없습니다."

# ✅ 외부에 내보낼 함수들
__all__ = [
    "get_vectorstore",
    "get_retriever",
    "get_retrieval_qa",
    "match_scenario_answer",
    "find_best_matching_answer"
]