import chromadb

from indexing import sync_index


client = chromadb.PersistentClient(path="./test_chroma")

collection = client.get_or_create_collection(
    name="brain_memories"
)

result = sync_index(
    memories_dir="./memories",
    collection=collection,
)

print("Sync result:")
print(result)

print("\nStored records:")
print(collection.get(include=["documents", "metadatas"]))