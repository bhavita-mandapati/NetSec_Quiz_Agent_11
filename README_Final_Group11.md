
# 🧠 **Group 11 – Agent-Based Intelligent Tutor for Network Security**

## **1. Project Overview**

This project implements an **Agent-Based Intelligent Tutor** for the *Network Security* course.  
It uses two local agents — a **Q&A Tutor Agent** and a **Quiz Agent** — built on a **Retrieval-Augmented Generation (RAG)** architecture.  
All processing occurs **entirely on the local system**, ensuring that no sensitive course data leaves the host machine.

- **Q&A Tutor Agent**: Answers course-related questions with accurate citations from lecture slides, textbooks, and notes.  
- **Quiz Agent**: Generates and grades Multiple-Choice, True/False, and Open-Ended questions with feedback.  
Both agents strictly follow the **privacy-preserving** mandate and provide transparent, verifiable outputs.

---

## **2. Required Environment**

- **Python** 3.10 or higher  
- **Hardware**: 8 GB RAM (recommended), local storage ≥ 1 GB  
- **OS**: macOS, Windows, or Linux  

---

## **3. Adopted Libraries**

| Library | Purpose |
|----------|----------|
| `chainlit` | Framework for chat-based UI interaction |
| `langchain` | Core LLM orchestration, retrieval, and RAG pipeline |
| `chromadb` | Vector database for local document embeddings |
| `huggingface_hub` / `sentence-transformers` | Local embeddings (MiniLM) |
| `pypdf` / `Unstructured` loaders | PDF/PPTX file parsing |
| `os` | System-level file operations |
| `dotenv` | Secure API key management (optional for local models) |

Install all dependencies:

```bash
pip install chainlit langchain chromadb openai pypdf python-dotenv sentence-transformers
```

---

## **4. System Architecture**

The system follows a modular **RAG** design consisting of:

### **4.1 Core Components**

1. **Document Loader (ingest.py):**
   - Loads lecture slides, textbooks, and quiz materials.  
   - Splits documents into semantic chunks and embeds them into a Chroma database.

2. **Vector Store (db/):**
   - Stores document embeddings locally for efficient retrieval.

3. **LLM Handler (response.py):**
   - Uses a local or offline LLM (via Ollama or ChatOpenAI) to generate responses.  
   - Returns answers with source citations.

4. **Quiz Agent (quiz_agent.py):**
   - Generates MCQ, True/False, and Open-Ended questions.  
   - Grades answers and provides cited feedback.

5. **UI Layer (Chainlit):**
   - Provides a browser-based chatbot interface for both Q&A and Quiz agents.

---

## **5. Flow of Execution**

### **Message Handling**

- The `@cl.on_message` decorator triggers whenever a new message is received in the chat UI.

### **Main Function**
```python
@cl.on_message
async def main(message: cl.Message):
    response = llm(message.content)
    await cl.Message(content=response).send()
```

### **LLM Function**
- Configures local embeddings  
- Connects to local vector store (`db/`)  
- Retrieves the most relevant context chunks  
- Generates and returns answers with citations  

### **loadResourceDocuments()**
- Loads and vectorizes lecture slides, textbooks, and quizzes.  
- Uses Chroma for persistent storage and future reuse.

---

## **6. Privacy-Preserving Design**

- **All computation** and **data storage** are local.  
- No text, document content, or embeddings are sent over external APIs.  
- **Wireshark captures** confirm all traffic remains within `127.0.0.1`.  
- (Optional) Google Search API may be used for public threat data, but never transmits course text.

---

## **7. How to Run**

### **Step 1 – Create Virtual Environment**
```bash
cd ~/Desktop/group11_prototype
python3 -m venv .venv
source .venv/bin/activate
```

### **Step 2 – Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3 – Ingest Lecture Slides**
```bash
python src/ingest.py
```

### **Step 4 – Run the Tutor**
```bash
chainlit run src/app.py -w
```
Browser will open at [http://localhost:8000](http://localhost:8000).

---

## **8. Example Usage**

### **For Q&A Tutor Agent**
**Prompt:**  
> “Explain the CIA triad and give one example for each component.”  
**Response:**  
> “Confidentiality protects sensitive data, Integrity ensures accuracy, and Availability maintains access. (Lecture_1_slides.pdf:4–6)”

### **For Quiz Agent**
**Prompt:**  
> “Generate 3 multiple-choice and 2 open-ended questions about symmetric encryption.”  
**Response:**  
> Generates questions with correct answers, rationales, and citations.

---

## **9. Capturing Prompts for Submission**

Each team member ran 5 prompts for verification:  
1. Record the chatbot answer screenshot (with citations).  
2. Record a Wireshark screenshot (showing 127.0.0.1 loopback traffic).  
3. Save the capture as `studentname.pcp`.  
4. Fill the provided `studentname.docx` template with all five prompts, answers, and trace summaries.

---

## **10. Common Issues**

| Issue | Cause | Solution |
|-------|--------|-----------|
| API Key error | OpenAI key not configured | Use `.env` file or switch to local model (Llama via Ollama) |
| No responses in chat | Vector DB not built | Run `python src/ingest.py` |
| Slow inference | Large slides | Reduce chunk size or limit query scope |
| External traffic warning | Optional tool misconfigured | Disable Google Search API |

---

## **11. Feedback and Improvements**

Future enhancements include:
- Adaptive question difficulty adjustment  
- Graph-based topic visualization  
- Wireshark integration in the Chainlit dashboard for live proof of locality  
- Support for multiple users and session logs

---

## **12. Command Summary**

```bash
# Environment setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build local DB
python src/ingest.py

# Launch chatbot
chainlit run src/app.py -w
```

---

✅ **Submission Files**
```
group11_prototype.zip
│
├── src/
│   ├── app.py
│   ├── ingest.py
│   ├── quiz_agent.py
│   └── response.py
│
├── db/ (vector database)
├── captures/ (Wireshark & docx files)
├── README.md
└── requirements.txt
```
