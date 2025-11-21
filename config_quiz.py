# config_quiz.py
# Configuration for the QUIZ AGENT (separate from Q&A agent)

# Folder paths for this Quiz Agent only
DATA_DIR = "data"
DB_DIR = "db"

# Vector DB name for Quiz Agent
COLLECTION_NAME = "netsec_quiz_docs"

# Local embedding model (does NOT touch Q&A agent)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking for splitting content into searchable parts
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Default quiz format
DEFAULT_NUM_MCQ = 3
DEFAULT_NUM_TF = 3
DEFAULT_NUM_OPEN = 2

ENABLE_WEB_CITATIONS = False
