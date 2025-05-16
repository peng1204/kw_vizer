import chromadb
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

import asyncio
import chromadb

async def main():
    clinet  = await chromadb.AsyncHttpClient()

    collection = await clinet.create_collection(name="my_collection")
    await collection.add(
        documents=["hello world"],
        ids=["id1"]
    )
asyncio.run(main())

