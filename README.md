*This project has been created as part of the 42 curriculum by aberrami*
# RAG Against the Machine

A Retrieval-Augmented Generation (RAG) system built for the 42 School **RAG Against the Machine** project.

The application indexes a local repository (documentation and source code), retrieves the most relevant chunks using BM25 lexical search, and generates answers after providing context using **Qwen3-0.6B**.

---

# Features

- Repository indexing
- Markdown and source code parsing
- Python AST-aware chunking
- BM25 lexical retrieval
- two-stage retrieval with neural reranking.
- Identifier-aware tokenizer
- Dataset search evaluation
- Recall@k evaluation
- Question answering using Qwen3-0.6B
- Batch answer generation
- Local LLM inference via vLLM

---

# Architecture

```
                    Repository
                         │
                         ▼
                File Discovery
                         │
                         ▼
                 File Processing
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
 Markdown Chunker                Python AST Chunker
         │                               │
         └───────────────┬───────────────┘
                         ▼
                   Chunk Collection
                         │
                         ▼
                 Identifier Tokenizer
                         │
                         ▼
                     BM25 Index
                         │
         ┌───────────────┴────────────────┐
         ▼                                ▼
     search                         search_dataset
         │                                │
         ▼                                │
Reranke top-k chunks                      │
         │                                │
         ▼                                ▼
    Top-k Chunks                   Search Results
         │                                │
         └───────────────┬────────────────┘
                         ▼
                 Prompt Construction
                         │
                         ▼
                  Qwen3-0.6B LLM
                         │
                         ▼
                      Answers
```

---

# Project Structure

```
src/student/

├── ingestion/
│   ├── chunker.py
│   ├── indexer.py
│   └── ...
|
├── datasets/
│   └── loader.py
│
├── evaluation/
│   ├── evaluator.py
│   ├── overlap.py
│   └── recall.py
│
├── generation/
│   ├── answer.py
│   ├── answer_dataset.py
│   ├── prompts.py
│   └── qwen.py
│
├── models/
│   ├── chunk.py
│   └── dataset.py
│
├── retrieval/
│   ├── search.py
│   ├── search_dataset.py
│   ├── tokenizer.py
│   └── ...
│
├── utils/
│
└── __main__.py
```

---

# Technologies

- Python 3.12+
- uv
- bm25s
- transformers
- torch
- tree-sitter / ast
- Pydantic
- tqdm

---

# Installation

Clone the repository.

```bash
git clone <repository>
cd rag-against-the-machine
```

Install dependencies.

```bash
uv sync
```

---

# Indexing

Build the searchable index.

```bash
uv run python -m student index
```

This performs:

- repository traversal
- markdown parsing
- python parsing
- chunk generation
- tokenization
- BM25 index construction
- Retrieval with neural reranking

Generated files are stored inside:

```
data/processed/
```

---

# Search

Search the indexed repository.

```bash
uv run python -m student search \
"What HTTP endpoint is used to dynamically load a LoRA adapter in vLLM?"
```

Example output:

```
Rank 1

File:
docs/features/lora.md

Score:
13.81

Content:
...
```

---

# Dataset Search

Generate retrieval results for an evaluation dataset.

```bash
uv run python -m student search_dataset \
--dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
--save_path data/output/search_results/docs_public.json
```
Example output:
```json
{
"search_results": [
        {
                "question_id": "q1",
                "retrieved_sources": [
                        {
                                "file_path": "docs/serving/openai_compatible_server.md",
                                "first_character_index": 9867,
                                "last_character_index": 10100
                        },
                        {
                                "file_path": "vllm/entrypoints/openai/api_server.py",
                                "first_character_index": 267,
                                "last_character_index": 400
                        }
                ]
        }
],
"k": 10
}
```

# Evaluation

Evaluate retrieval quality.

```bash
uv run python -m student evaluate \
--student_answer_path data/output/search_results/docs_public.json \
--dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
```

Example output:

```
🎯 Evaluation Results
========================================
Questions evaluated: 100
Recall@1: 0.710
Recall@3: 0.830
Recall@5: 0.870
Recall@10: 0.870
```

---

# Question Answering

Ask questions about the indexed repository.

```bash
uv run python -m student answer \
"What HTTP endpoint is used to dynamically load a LoRA adapter in vLLM?"
```

Example answer:

```
The `/v1/load_lora_adapter` endpoint is used to dynamically load a LoRA adapter in vLLM. A POST request should be sent to this endpoint with the adapter name and path provided in the JSON payload.
```

---

# Batch Answer Generation

Generate answers for an entire dataset.

```bash
uv run python -m student answer_dataset \
--search_results_path data/output/search_results/docs_public.json \
--save_path data/output/answers/docs_public.json
```
Example answer:
```json
"search_results": [
        {
                "question_id": "q1",
                "retrieved_sources": [
                        {
                                "file_path": "docs/serving/openai_compatible_server.md",
                                "first_character_index": 9867,
                                "last_character_index": 10100
                        },
                        {
                                "file_path": "vllm/entrypoints/openai/api_server.py",
                                "first_character_index": 267,
                                "last_character_index": 400
                        }
                ],
                "answer": "To configure the OpenAI compatible server in vLLM..."
        }
],
"k": 10
```
---

# Retrieval Strategy

The retrieval pipeline is based on lexical search using BM25.

Pipeline:

1. Query tokenization
2. BM25 retrieval
3. Neural reranking.
4. Top-k chunk selection
5. Context construction
6. Prompt generation
7. LLM inference

---

# Chunking Strategy

## Markdown

Markdown files are split by headings while preserving section hierarchy.

Advantages:

- semantic chunks
- minimal context fragmentation
- good retrieval quality

---

## Python

Python files are parsed using the Abstract Syntax Tree (AST).

Chunks correspond to:

- classes
- functions
- methods

Additional metadata is included:

- file path
- class name
- function name

This significantly improves lexical retrieval.

---

# Identifier-aware Tokenization

Standard tokenization performs poorly on source code because identifiers are compound words.

Examples:

```
KVCacheManager

↓

kv
cache
manager
kvcachemanager
```

```
AsyncLLMEngine

↓

async
llm
engine
asyncllmengine
```

This allows natural language queries such as:

```
cache manager
scheduler
gpu worker
```

to match identifiers appearing in the source code.

Identifier-aware tokenization was the single largest improvement in retrieval quality.

---

# Prompting Strategy

The LLM receives:

- retrieved chunks
- question
- instructions to answer only from the supplied context

Prompt structure:

```
System

↓

Context

↓

Question

↓

Answer
```

The model is instructed not to hallucinate and to answer only using the retrieved evidence.

---

# Model

Model:

```
Qwen/Qwen3-0.6B
```

Generation:

- deterministic decoding
- greedy search
- no sampling

This provides reproducible outputs suitable for evaluation.

---

# Results

Final public evaluation:

## Documentation

```
Recall@1: 0.710
Recall@3: 0.830
Recall@5: 0.870
Recall@10: 0.870
```

Requirement:

```
Recall@5 ≥ 0.80
```

Status:

**PASS**

---

## Code

```
Recall@1  = 0.51
Recall@3  = 0.73
Recall@5  = 0.78
Recall@10 = 0.84
```

Requirement:

```
Recall@5 ≥ 0.50
```

Status:

**PASS**

---

# Performance

Retrieval is entirely based on a pre-built BM25 index.

Search latency is typically well below one second.

Most execution time is spent during LLM generation.

---

# Design Decisions

The system intentionally separates retrieval from generation.

Advantages:

- independent evaluation
- reproducible retrieval
- modular architecture
- reusable search results
- easier debugging
- simpler benchmarking

This separation also allows experimenting with different language models without rebuilding the retrieval index.

---
# Challenges Faced

As this was my first time building a Retrieval-Augmented Generation (RAG) system, I encountered a steep learning curve. 

**Key Challenges:**
* **Conceptual Research:** Spending foundational time understanding the underlying mechanics before writing code.
* **Pipeline Integration:** Managing data flow across the entire lifecycle, including text chunking, database indexing, vector retrieval, and LLM prompt generation.

# Resources
## Web 
Youtube videos was the main ressouce to explain some new concepts like rag, bm25 indexing and many other tools used to build this project like:

-[What is Retrieval-Augmented Generation (RAG)? ](https://www.youtube.com/watch?v=T-D1OfcDW1M)

-[BM25 ](https://www.youtube.com/watch?v=hiJcEaiuw_E)

## Use of Artificial Intelligence

Artificial Intelligence tools were used throughout the project as a development assistant. All design decisions, implementation, testing, debugging, and validation were reviewed and integrated by the author.

AI assistance was used for the following tasks:

- Explaining concepts related to Retrieval-Augmented Generation (RAG), BM25, tokenization, and prompt engineering.
- Understanding the architecture and source code of the vLLM project.
- Discussing software architecture and component organization.
- Reviewing Python implementations and suggesting refactoring opportunities.
- Assisting in debugging runtime errors and improving error handling.
- Helping design the command-line interface and project structure.
- Brainstorming retrieval improvements, including identifier-aware tokenization and hybrid retrieval strategies.
- Reviewing prompt design for Qwen3-0.6B and improving answer generation quality.
- Assisting in writing and proofreading the project documentation and README.

AI-generated content was always reviewed, adapted, tested, and integrated manually before being included in the final project.