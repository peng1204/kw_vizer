import chromadb
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
print(chroma_client.list_collections()) # collection 목록 가져오기

collection = chroma_client.create_collection(name="new_collection")
print(chroma_client.list_collections())