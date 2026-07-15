def retrieve_memories(
    collection,
    query: str,
    limit: int = 5,
    filters: dict | None = None,
) -> list[dict]:
    """
    Search ChromaDB for memories most relevant to the query. Using Euclidean distance.
    """
    if not query.strip():
        return []

    results = collection.query(
        query_texts=[query],
        n_results=limit,
        where=filters,
        include=["documents", "metadatas", "distances"],
    )

    memories = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    for memory_id, content, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        memories.append(
            {
                "id": memory_id,
                "content": content,
                "metadata": metadata or {},
                "distance": distance,
            }
        )

    return memories


def retrieve_task_memory(
    collection,
    task_id: str,
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Retrieve only memories belonging to a specific task.
    """
    filters = {
        "$and": [
            {"type": "task_state"},
            {"task_id": task_id},
        ]
    }

    return retrieve_memories(
        collection=collection,
        query=query,
        limit=limit,
        filters=filters,
    )


def build_context_block(memories: list[dict]) -> str:
    """
    Convert retrieved memories into text for Claude's context.
    """
    if not memories:
        return ""

    lines = ["## Relevant Brain Memories"]

    for memory in memories:
        content = memory.get("content", "").strip()
        metadata = memory.get("metadata", {})
        source = metadata.get("file_path", "unknown")

        lines.append(f"- {content}\n  Source: {source}")

    return "\n".join(lines)

# I will use cosine similarity to retrieve memories.
# We care about query and memory similarity, not just magnitude.
# cosine works well for text emebedding of different lengths.
# Euclidean distance is good for vector magnitude.
# Dot product cna favor embedding with larger magnitude unless normalized.
# weakness of cosine is that simialr direction not always = to identifcal meaning 
# for example 
# Mem1: "User sorta likes spicy food"
# Mem2: "User loves extremely hot and spicy food"
# Both have similar direction so cosine rank them identical but strength is different.
# also recency might be diff sorta liked 2 years ago vs just now loves.
# We could also combine cosine and euclidean distance to get the best of both worlds.
# but to avoid over complex, we will solve this problem by
# combining with 
# metadata filters like repository, team, task, and memory type
# a minimum similarity threshold
# retrieving top-k candidates, then reranking them
# limiting how many memories are injected