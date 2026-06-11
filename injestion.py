def add_to_memory(text: str, metadata: dict):
    payload = {"content": text}
    if metadata:
        payload["metadata"] = metadata
    # need a memory client to handle embedding, indexing, and persistence
    memory = mem_client.create_memory(payload)
    return memory

