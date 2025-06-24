# check_vectorstore.py
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import qa_chain

ko_embedding = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    model_kwargs={"device": "cpu"}
)

vectorstore = Chroma(
    persist_directory="./data/chroma_db",
    collection_name="lecture_search",
    embedding_function=ko_embedding
)

print("총 문서 수:", vectorstore._collection.count())
docs = vectorstore.as_retriever().get_relevant_documents("조민수")
print("[🔍 검색 결과 미리보기]", docs[:1])
