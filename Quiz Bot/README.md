# Chatbot Project (Flask + LangChain + ChromaDB + Ollama)

This is a ready-to-run scaffold that uses your **`server.py`** and **`vectorization.py`**.
It ingests PDFs into a Chroma vector store and serves a Flask API for question-answering
with LangChain RetrievalQA and a local LLM via Ollama.

## Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running: `ollama serve`
- A local model pulled (for example): `ollama pull llama3.1`
- Some PDFs in `./data/` to index

## Setup

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
mkdir -p data chroma_db
```

**Edit `.env`** if you want to change `CHROMA_DIR`, `DATA_DIR`, or `OLLAMA_MODEL`.

## Build the vector index

```bash
python vectorization.py
```
This should read PDFs from `DATA_DIR` (`./data` by default) and write a Chroma
DB to `CHROMA_DIR` (`./chroma_db` by default).

> If you get embedding/LLM errors, double‑check that `ollama serve` is running
> and that `OLLAMA_MODEL` exists locally (`ollama list`).

## Run the API server (Flask)

### Development
```bash
export FLASK_APP=server.py
flask run --port 8000 --debug
```
or
```bash
python server.py
```

### Production (Gunicorn)
```bash
gunicorn -w 2 -b 0.0.0.0:8000 server:app
```

## Example API usage

Assuming the server is running at `http://localhost:8000`.

### Ask a question
```bash
curl -X POST http://localhost:8000/ask   -H "Content-Type: application/json"   -d '{"question":"What is zero trust?", "k": 4}'
```

### Rebuild index
```bash
curl -X POST http://localhost:8000/reindex
```

> Endpoints may vary slightly depending on how your `server.py` routes are written.
> The above are common choices. Inspect `server.py` to see the exact paths and fields.

## Docker (optional)

**Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \    build-essential \    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "server:app" ]
```

**docker-compose.yml** (runs app + Ollama)
```yaml
version: "3.9"
services:
  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama

  app:
    build: .
    depends_on:
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db

volumes:
  ollama:
```

Then:
```bash
docker compose up --build
```

## Notes & Troubleshooting

- **FAISS vs Chroma**: Your code uses **Chroma** as the vector store. No external DB is required; it persists to disk.
- **Embeddings**: If using HuggingFace embeddings, models may download on first run. If using Ollama for embeddings, ensure the model supports it.
- **CUDA**: This setup is CPU‑friendly. For GPU acceleration with sentence-transformers, install PyTorch with the right CUDA wheel before `pip install -r requirements.txt`.
- **Windows**: If `faiss-cpu` fails to install, remove it from `requirements.txt` (not needed for Chroma) or install via conda.

---

Happy hacking!
