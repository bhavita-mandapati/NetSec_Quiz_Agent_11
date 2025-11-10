# GROUP11  Prototype Submission



## Project Title
Local Network-Security Tutor & Quiz Bot (Privacy-Preserving)

## Objective
Agent-based tutor that (1) answers course questions with **citations** from local docs and (2) generates & grades quizzes (MCQ, T/F, Open-Ended). **All training and inference run locally**; optional web citations are added only when externally requested.

## System Architecture
- **RAG** with local vector store (**Chroma/FAISS**) and local embeddings (Sentence-Transformers).
- **LLM:** local-first (Ollama Llama 3 if available) or `llama-cpp-python`. OpenAI **disabled by default**.
- **Agents:**
  - **Q&A Tutor Agent:** retrieve → synthesize → verify (citations with filename + page/chunk).
  - **Quiz Agent:** build quizzes (random/topic), grade open-ended semantically, return feedback with citations.
- **UI:** Chainlit chat app.

See `slides/group11_round2.pptx` for visuals, and `system/systemarchitecture.png`.

## Prerequisites
- Python 3.10+
- (Optional) Ollama installed locally with `llama3` pulled
- C++ build tools (for faiss-cpu on some platforms)

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Data
Place your **local course materials** (PDF/PPTX) in `data/`. Nothing leaves your machine.

## Build the Vector DB
```bash
python src/ingest.py --data_dir data --persist_dir db --chunk_size 1000 --chunk_overlap 100
```

## Run the App
```bash
# (optional) export OLLAMA_HOST=http://127.0.0.1:11434
chainlit run src/app.py -w
```

## Configuration
- `config/local.yaml` – privacy defaults (no external APIs).
- `chainlit/config.toml` – UI settings.
- `.env` – leave empty unless you explicitly enable web search (off by default).

## Adopted Libraries
- chainlit, langchain, chromadb, faiss-cpu
- pypdf, unstructured, python-docx, python-pptx
- sentence-transformers, tqdm
- (optional) ollama, llama-cpp-python

## Flow of Execution
1. **Ingest**: load PDFs/PPTXs → chunk → embed (local) → persist to Chroma/FAISS.
2. **Q&A**: user asks → retrieve top-k → compose final answer (local LLM) → **append citations**.
3. **Quiz**: generate MCQ/T/F/Open-Ended from retrieved chunks → accept answers → grade → **return feedback** with citations.
4. **(Optional)** Web search tool can add current threat intel citations—disabled by default to preserve privacy.

## Commands
```bash
# Ingest data
python src/ingest.py --data_dir data --persist_dir db

# Run Chainlit app
chainlit run src/app.py -w

# Run quick console test
python src/test_cli.py "Explain TLS handshake"
```

## Issues & Solutions
- **OpenAI key in legacy code**: Removed. Use **local models** to meet privacy mandate.
- **Vector DB empty**: Run `ingest.py` and ensure `data/` has files.
- **Large PDFs**: Adjust `--chunk_size` and `--chunk_overlap`. Use `--max_docs` to test quickly.

## Suggestions & Feedback
- Add a **security monitor** to assert no outbound requests during RAG.
- Add **Wireshark trace** to demonstrate local-only traffic for bonus points.
- Extend loaders to include quizzes and slides metadata for better quiz generation.

## License
Academic use for course submission.
