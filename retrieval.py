import injestion 


def retrieve_memories(query: str, limit: int=5):
    # retrieve memory from vector database with search memory
    # why do we need a limit?
    memories = mem_client.search_memory(
        {
            "query": query,
            "limit": limit,
        }
    )
    return memories

# retrive for specfic tasks only
def retrieve_task_memory(task_id: str, query: str):
    memories = mem_client.search_memory(
        {
            "query": query,
            "filters": {
                "metadata.type": "task_state"
                "metadata.task_id": task_id
            },
        }
    )
    return memories

# Build context block
# Take a list of memory dicts and returns a single string
"""
Input: 
[
  {"content": "likes spicy food", "metadata": {"type": "preference"}},
  {"content": "lives in Waterloo", "metadata": {"type": "fact"}}
]

Output:
- likes spicy food (meta: {'type': 'preference'})
- lives in Waterloo (meta: {'type': 'fact'})
"""
def build_context_block(memories: list[dict]) -> str:
    context = ""
    lines = []
    if not memories:
        return ""
    for line in memories:
        content = mem.get("content", "")
        metadata = mem.get("metadata", {})
        lines.append(f"-{content} (meta: {metadata})")
    return "\n".join(lines)

def agent_reply(user_message: str) -> str:
    memories = mem_client.retrieve_memories(user_message, limit)
    memory_block = build_context_block(memories)
    prompt = []
    sys_prompt = "You are a friendly helpful assistant, use what you know about the user from memories"
    prompt.append(sys_prompt)
    if memory_block:
        prompt.append("\nMemories:\n" + memory_block)
    prompt.append("\nUser message:\n" + user_message)

    final_prompt = "\n".join(prompt)
    response = call_llm(final_prompt)

    store_user_memory(text=f"User said: {user_message}", metadata={"type": "message"})
    return response
    
    