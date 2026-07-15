Components of Long term memory
Ingestion Pipeline: NLP to determine what events and facts from conversations we should keep, convert them into normalized memory entries.
Storage backend: Persists memory by vector store with embeddings. Chucks of text into vector database, inference call retrieves top k most similar items to current query. 
Retrieval engine: Retrieves relevant memories based on semantic similarity, metadata filters, importancy scoring
Summarization: Compresses longer histories into summaries 
Prompt integration: Injects retrieved memory into prompts. System messages for long lived facts, and context section for recent or situational memories

Brain VS Mem0
1. Git as sync layer: no api keys, no database, no infra, no onboarding. A team can adopt through one PR. Mem0 is external service and you trust it with your internal context
2. Markdown is autiable: Engineers and teams can go through memory and read it, vector dbs you can't go thru
3. Biggest differianter was the team memory bank but since I'm rebuilding for myself I'll keep it to a personal memory bank

My Brain rebuild
- Context budget aware retrieval: Embed memories, retrieve top k by relevance to current task only inject those
- Automatic memory extraction: watch session end and extract candidate memroies automatically
- Keep markdown as source of truth and embeddings as the index 


1st design descision
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

# design decision
#     Important design decision

# Retention should depend on memory type:

# Architecture/coding conventions: keep until superseded
# Preferences: keep until updated or removed
# Task state: short TTL
# Temporary investigation notes: expire after a set period
# Conversation summaries: retain only when they remain useful

# So we should add fields like:

# expires_at
# retention_policy
# sensitivity
# requires_consent