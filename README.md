Components of Long term memory
Ingestion Pipeline: NLP to determine what events and facts from conversations we should keep, convert them into normalized memory entries.
Storage backend: Persists memory by vector store with embeddings. Chucks of text into vector database, inference call retrieves top k most similar items to current query. 
Retrieval engine: Retrieves relevant memories based on semantic similarity, metadata filters, importancy scoring
Summarization: Compresses longer histories into summaries 
Prompt integration: Injects retrieved memory into prompts. System messages for long lived facts, and context section for recent or situational memories
