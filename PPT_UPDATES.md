# Slide Content — Exact Text (Pages 2–6)

Page 1 (title/team) unchanged. Paste the following verbatim into each slide.

---

## Page 2 — Problem Statement

**Title:** Problem Statement

**Subheading:** The Challenge

**Body:** Support engineers often need to investigate newly reported incidents by searching historical tickets.

**Bullets:**
- Large volume of historical tickets
- Manual searching is time-consuming
- Similar incidents may be difficult to identify
- Keyword search fails on vocabulary gaps — e.g. "NPE" vs "NullPointerException", "consumer stuck" vs "rebalance loop"
- Root causes and resolutions are scattered across tickets
- LLMs can hallucinate unsupported root causes

**Flow diagram:**
```
New Incident → Search Historical Tickets → Identify Similar Cases → Analyze RCA → Resolve
```

**Goal line:** Reduce investigation time while keeping RCA grounded in historical evidence.

---

## Page 3 — Our Solution

**Title:** Our Solution

**Subheading:** Features

**Bullets:**
- Historical CSV dataset upload
- New incident description
- Top 5 similar incidents
- Similarity scores
- Root cause & resolution
- Concise AI-generated RCA
- Evidence-based fallback

**Sub-line:** No sufficient evidence → Not explicitly documented.

**Tech Stack:**
| Backend | Retrieval | AI / RAG | Frontend | Data |
|---|---|---|---|---|
| Python, FastAPI, Uvicorn | Sentence Transformers (all-MiniLM-L6-v2), FAISS | LangChain, LangGraph, Groq (openai/gpt-oss-120b) | React, JavaScript, Tailwind CSS | Pandas, Apache Jira historical incidents |

**Visual:** Screenshot of the live app — Root Cause Analysis panel + Similar Historical Incidents panel, showing a real analyzed incident (ticket ID, similarity meter, root cause, resolution, AI summary, confidence badge).

---

## Page 4 — System Architecture

**Title:** System Architecture

**Dataset block:**
```
Dataset: 3,000 curated incidents across 8 Apache projects
Projects: Cassandra, Flink, Hadoop, HBase, Kafka, Solr, Spark, ZooKeeper (375 records each)
Source: public Zenodo dataset (Apache Jira issues)
Fields: ticket_id, project, summary, description, components, labels, comments,
        root_cause, resolution_status, resolution_notes, root_cause_source,
        resolution_source, evidence_quality, search_text
Note: resolution_status (Jira workflow state) is never treated as evidence —
      only resolution_notes is.
```

**Storage block:**
```
Storage: No traditional database.
File-based FAISS index (3,000 × 384-dim vectors, ~4.6 MB) + metadata.pkl (~23 MB).
```

**Diagram 1 — Ingestion:**
```
HISTORICAL DATA CSV → CSV Validation → Data Cleaning → Search Text Creation
→ Sentence Transformer (MiniLM Embeddings) → FAISS Index
```

**Diagram 2 — Query:**
```
New Incident → Retrieval → Top 10 Candidates → Reranking → Top 5 → Evidence Check
   Evidence Check ──sufficient──→ LLM → Validation → Final RCA
   Evidence Check ──insufficient──→ "Not explicitly documented"
```

---

## Page 5 — AI-Powered RCA Pipeline & Results

**Title:** AI-Powered RCA Pipeline & Results

**Subheading:** Finding the Most Relevant Incidents

**Stage 1 — Semantic Retrieval**
Sentence Transformer: all-MiniLM-L6-v2
- Converts incidents into 384-dimensional vectors
- FAISS retrieves Top 10 candidates
- Captures meaning beyond exact keywords

**Stage 2 — Reranking**
Final score:
- 70% Semantic Similarity
- 15% Technical-Term Overlap
- 15% Keyword Overlap
→ Final Top 5 Similar Incidents

**Where AI Is Used:**
| Layer | Technology | Purpose |
|---|---|---|
| ML | MiniLM | Semantic embeddings |
| Retrieval | FAISS | Similar incident search |
| Reranking | Weighted scoring | Improve technical relevance |
| GenAI | Groq / GPT-OSS 120B | RCA synthesis |
| Orchestration | LangGraph | Evidence gating, citation validation |

**LangGraph Workflow:**
```
START → Analyze → Retrieve → Rerank → Evidence Check
   Evidence Check ──sufficient──→ Generate RCA → Validate → END
   Evidence Check ──insufficient──→ "Not explicitly documented" → END
```

**Results — Measured on the Real Pipeline:**
| Metric | Result |
|---|---|
| Recall@5 | 0.875 |
| MRR | 0.875 |
| Hallucination rate | 0.0 |
| Evidence-support rate | 1.0 |
| Abstention correctness (out-of-domain query) | 1.0 |
| Root-cause correctness | 0.67 |

**Caption:** Evaluated end-to-end across all 8 projects plus 1 out-of-domain control query, through the real pipeline — embeddings → FAISS → rerank → LangGraph → Groq.

---

## Page 6 — What Makes This Different / Future Scope / Related Research

**Title:** What Makes This Different

**Bullets:**
- No semantic leakage — root_cause and resolution are excluded from the embedded search text
- Workflow status ≠ resolution — "Fixed/Closed" is never treated as a technical fix
- Explainable reranking — fixed, visible weights, not a black box
- Two deterministic anti-hallucination gates — evidence-alignment check before generation, citation + mechanism-match validation after
- Every claim cited to a real ticket ID

**Subheading:** Future Scope
- Hybrid retrieval using BM25 + vector search
- Managed vector database such as Qdrant / pgvector
- Engineer feedback loop for improving ranking
- Real-time integration with monitoring/alert systems
- Automated regression evaluation
- Larger incident knowledge base

**Subheading:** Related Research: Historical Incident Retrieval & RAG-Based RCA

**Saha & Hoi (2022), Mining Root Cause Knowledge from Cloud Service Incident Investigations for AIOps**
Uses knowledge from historical incident investigations for automated RCA.

**Xu et al. (2024), RAG with Knowledge Graphs for Customer Service QA**
Retrieves relevant information from historical customer-service issues and uses it to generate answers.
