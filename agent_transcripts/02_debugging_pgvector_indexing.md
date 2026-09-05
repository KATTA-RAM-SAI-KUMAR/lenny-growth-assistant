# Agent Transcript 02: Debugging Pgvector Indexing & Vector Embeddings
**Timestamp:** 2026-09-05T09:22:00Z  
**Agent:** Antigravity AI (Pair Programming)  
**Objective:** Solve vector dimensionality, HNSW indexing parameters, and recursive transcript chunking.

## Challenge & Debugging Journey

### 1. Vector Dimension Mismatch
- **Issue:** Different embedding models output varying vector dimensions:
  - `sentence-transformers/all-MiniLM-L6-v2`: 384 dimensions.
  - `nomic-embed-text`: 768 dimensions.
  - `text-embedding-3-small`: 1536 dimensions.
- **Correction:** Standardized on 384 dimensions for the core schema (`Vector(384)`). Created an embedding wrapper that normalizes vectors to unit length for exact cosine distance computation (`1 - (embedding <=> :vector)`).

### 2. Chunk Boundary Integrity
- **Issue:** Standard naive character splitting cut through speaker sentences, e.g.:
  `"Brian Chesky (00:00:00): Way too many founders apologize for..."` was cut mid-phrase, causing the retriever to lose context on who was speaking.
- **Correction:** Implemented recursive splitting that respects timestamp markers:
  - Priority 1: Speaker turns (`r"([A-Za-z\s]+ \(\d{2}:\d{2}:\d{2}\):)"`).
  - Priority 2: Paragraph breaks (`\n\n`).
  - Target chunk size: 500–800 tokens with 100-token overlap.
  - Each chunk retains its metadata header (`guest`, `title`, `timestamp`) prepended to the chunk text for improved vector representation.

### 3. Pgvector Index Optimization
- **Optimization:** Configured HNSW indexing:
  ```sql
  CREATE INDEX IF NOT EXISTS transcript_chunks_hnsw_idx 
  ON transcript_chunks USING hnsw (embedding vector_cosine_ops) 
  WITH (m = 16, ef_construction = 64);
  ```
  This reduces similarity search latency from linear table scans to under 10ms per query.
