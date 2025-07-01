import os, json
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import chromadb
import pdfplumber

# === 임베딩 모델 설정 ===
ko_embedding = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask", 
    model_kwargs={"device": "cpu"}
)

base_path = "./data"
chroma_path = f"{base_path}/chroma_db"
client = chromadb.PersistentClient(path=chroma_path)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
embeddings_model = ko_embedding

def load_json_documents_with_summary(json_files):
    docs = []
    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            # 기존 문서(질문-답변/수강이력/강의정보 등)
            if "Text" in item and "Completion" in item:
                docs.append(Document(
                    page_content=f"질문: {item['Text']}\n답변: {item['Completion']}",
                    metadata={"카테고리": item.get("카테고리", "")}
                ))
            if "lecture_name" in item and "student_id" in item:
                content = (
                    f"학번: {item['student_id']}\n"
                    f"강의명: {item['lecture_name']}\n"
                    f"학정번호: {item['lecture_id']}\n"
                    f"개설 학과: {item['department_offered']}\n"
                    f"이수 구분: {item['lecture_course_type']}\n"
                    f"학점: {item['lecture_credit']}학점\n"
                    f"성적: {item.get('lecutre_grade', '')}"
                )
                if "retake_or_delete_status" in item:
                    content += f"\n재수강/삭제 여부: {item['retake_or_delete_status']}"
                if "retake_status" in item:
                    content += f"\n재수강 여부: {item['retake_status']}"
                docs.append(Document(page_content=content))
            if "lecture_id" in item and "lecture_name" in item and "student_id" not in item:
                content = (
                    f"학정번호: {item.get('lecture_id', '')}\n"
                    f"강의명: {item.get('lecture_name', '')}\n"
                    f"강의평점: {item.get('lecture_ratings', '')}\n"
                    f"과제: {item.get('lecture_homework', '')}\n"
                    f"팀플: {item.get('lecture_team', '')}\n"
                    f"성적평가정도: {item.get('lecutre_grade', '')}\n"
                    f"출결 방식: {item.get('lecutre_attendance', '')}\n"
                    f"시험 횟수: {item.get('lecutre_test', '')}\n"
                    f"시험 방식: {item.get('lecture_testinform', '')}\n"
                    f"전공 학점: {item.get('credits_major', '없음')}\n"
                    f"교양 학점: {item.get('credits_general', '없음')}\n"
                    f"총 학점: {item.get('credits_total', '없음')}\n"
                    f"교수명: {item.get('lecture_professorname', item.get('lecture_professor', ''))}\n"
                    f"수업 시간: {item.get('lecture_time', '')}\n"
                    f"강의 유형: {item.get('lecture_course_type', '')}\n"
                    f"학점: {item.get('lecture_hours', '')}시간\n"
                    f"학기: {item.get('lecture_semester', '')}학기\n"
                    f"강의 설명: {item.get('lecture_inform', '')}\n"
                    f"영역: {item.get('lecture_domain', '')}\n"
                )
                docs.append(Document(page_content=content))
            # === flat summary ===
            if "lecture_name" in item and "lecture_professor" in item:
                summary = (
                    f"강의명: {item.get('lecture_name', '')} / 교수명: {item.get('lecture_professor', '')} / "
                    f"이수구분: {item.get('lecture_course_type', '')} / 학점: {item.get('lecture_credit', '')} / "
                    f"강의시간: {item.get('lecture_time', '')} / 수업유형: {item.get('lecture_system','')} / "
                    f"교양영역: {item.get('lecture_domain','')}"
                )
                docs.append(Document(page_content=summary))
    return [doc for doc in docs if doc.page_content and doc.page_content.strip()]

def embed_flat_lecture_collection():
    # 요약문 기반 flat 컬렉션
    flat_docs = []
    with open(os.path.join(base_path, "수강신청자료집.json"), encoding="utf-8") as f:
        lectures = json.load(f)
    for lec in lectures:
        if "lecture_name" in lec and "lecture_professor" in lec:
            flat_docs.append(
                f"강의명: {lec['lecture_name']} / 교수명: {lec['lecture_professor']} / "
                f"이수구분: {lec['lecture_course_type']} / 학점: {lec['lecture_credit']} / "
                f"강의시간: {lec['lecture_time']} / 수업유형: {lec.get('lecture_system','')} / "
                f"교양영역: {lec.get('lecture_domain','')}"
            )
    # 임베딩
    vs = Chroma.from_texts(
        flat_docs, ko_embedding, persist_directory=chroma_path, collection_name="lecture_flat"
    )
    print(f"✅ 요약문 기반 'lecture_flat' 컬렉션 임베딩 완료 ({len(flat_docs)}개)")

def embed_all_data():
    user_datasets = {
        "kim": [os.path.join(base_path, fname) for fname in [
            "김브티_수강이력.json", "김브티_성적.json", "Student.json"
        ]],
        "hong": [os.path.join(base_path, fname) for fname in [
            "홍데사_수강이력.json", "홍데사_성적.json", "Student.json"
        ]]
    }
    task_datasets = {
        "lecture_search": [os.path.join(base_path, fname) for fname in [
            "강의탐색.json", "강의 평점.json", "수강신청자료집.json",
            "커리큘럼(DS).json", "커리큘럼(VT).json", "강의계획서.json", "lecture_domain.json"
        ]],
        "career_counsel": [os.path.join(base_path, fname) for fname in [
            "진로상담.json", "수강신청자료집.json", "커리큘럼(DS).json",
            "커리큘럼(VT).json", "강의계획서.json"
        ]],
        "academic_status": [os.path.join(base_path, fname) for fname in [
            "학습현황.json", "김브티_수강이력.json", "홍데사_수강이력.json", "Student.json"
        ]]
    }
    existing = [c.name for c in client.list_collections()]
    # 사용자별 임베딩
    for user_id, files in user_datasets.items():
        collection_name = f"lecture_search_{user_id}"
        if collection_name in existing:
            print(f"[{collection_name}] 이미 임베딩됨. 생략.")
            continue
        docs = load_json_documents_with_summary(files)
        split_docs = text_splitter.split_documents(docs)
        texts = [doc.page_content for doc in split_docs]
        embeddings = embeddings_model.embed_documents(texts)
        collection = client.create_collection(name=collection_name)
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=[f"{collection_name}_{i}" for i in range(len(texts))]
        )
        print(f"[{collection_name}] 임베딩 완료: {len(texts)}건")
    # 기능별 임베딩
    for task, files in task_datasets.items():
        if task in existing:
            print(f"[{task}] 이미 임베딩됨. 생략.")
            continue
        docs = load_json_documents_with_summary(files)
        split_docs = text_splitter.split_documents(docs)
        texts = [doc.page_content for doc in split_docs]
        embeddings = embeddings_model.embed_documents(texts)
        collection = client.create_collection(name=task)
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=[f"{task}_{i}" for i in range(len(texts))]
        )
        print(f"[{task}] 임베딩 완료: {len(texts)}건")
    # PDF 임베딩
    pdf_files = [
        os.path.join(base_path, "강의시간표.pdf"),
        os.path.join(base_path, "수강신청_자료집_전체(2025-1)v4.pdf")
    ]
    for path in pdf_files:
        if os.path.exists(path):
            print(f"PDF 로딩 중: {os.path.basename(path)}")
            raw_texts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        raw_texts.append(text)
            docs = text_splitter.create_documents(raw_texts)
            texts = [doc.page_content for doc in docs]
            embeddings = embeddings_model.embed_documents(texts)
            for name in ["lecture_search", "career_counsel", "academic_status"]:
                collection = client.get_or_create_collection(name=name)
                collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    ids=[f"{name}_pdf_{i}" for i in range(len(texts))],
                    metadatas=[{"source": os.path.basename(path)} for _ in range(len(texts))]
                )
                print(f"[{name}] PDF 임베딩 추가 완료: {len(texts)}건")
        else:
            print(f"❌ PDF 파일을 찾을 수 없습니다: {path}")

if __name__ == "__main__":
    embed_all_data()
    embed_flat_lecture_collection()   # ★ flat summary 컬렉션도 생성
    print("임베딩 완료")
