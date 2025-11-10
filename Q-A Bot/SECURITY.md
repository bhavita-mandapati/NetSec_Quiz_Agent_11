# Security & Privacy Notes

- All retrieval and generation are **local-first**. No document text is sent to external APIs.
- The code uses **HuggingFace local embeddings** and **Ollama / llama-cpp** by default.
- `.env` is optional; avoid putting any API keys there.
- Consider recording a **Wireshark** capture during ingest/run to show zero outbound calls.
