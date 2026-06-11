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