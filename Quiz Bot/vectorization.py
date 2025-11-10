# from langchain import hub
# from langchain.chains import RetrievalQA
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# from langchain.callbacks.manager import CallbackManager
# from langchain.llms import Ollama
# from langchain.embeddings.ollama import OllamaEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import PyPDFLoader
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory
# import chromadb.utils.embedding_functions as embedding_functions
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# import streamlit as st
# import os
# import time
# import warnings
# warnings.filterwarnings('ignore')



# def getEmbeddings():
#     model_name = "BAAI/bge-small-en"
#     model_kwargs = {"device": "cpu"}
#     encode_kwargs = {"normalize_embeddings": True}
#     hf = HuggingFaceBgeEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
#     return hf

# files = [
#     "Lecture 1_slides-combined.pdf",
#     "Network_security_text_book.pdf"
# ]

# temp = []
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
# for i in files:
#     loader = PyPDFLoader(i)
#     data = loader.load()
#     all_splits = text_splitter.split_documents(data)
#     temp = temp + all_splits


# persist_directory = 'database'

# vectorstore = Chroma.from_documents(
#     documents=all_splits, embedding=getEmbeddings(),persist_directory=persist_directory)

# vectorstore.persist()
from langchain import hub
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.llms import Ollama
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import chromadb.utils.embedding_functions as embedding_functions
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import streamlit as st
import os
import time
import logging
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def getEmbeddings():
    """Initialize and return the HuggingFace embeddings model."""
    try:
        model_name = "BAAI/bge-small-en"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}
        hf = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        logger.info("Successfully initialized embeddings model")
        return hf
    except Exception as e:
        logger.error(f"Error initializing embeddings: {str(e)}")
        raise

def load_and_split_document(file_path):
    """Load and split a single document with proper metadata."""
    try:
        logger.info(f"Processing file: {file_path}")
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Load document
        loader = PyPDFLoader(file_path)
        data = loader.load()
        
        # Add source metadata to each page
        for page in data:
            page.metadata["source"] = os.path.basename(file_path)
            page.metadata["page"] = page.metadata.get("page", 0)
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        splits = text_splitter.split_documents(data)
        
        logger.info(f"Created {len(splits)} splits from {file_path}")
        return splits
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise

def verify_database(vectorstore):
    """Verify the database was created successfully and contains documents."""
    try:
        # Test a simple query
        results = vectorstore.similarity_search("test", k=1)
        
        # Log database statistics
        logger.info(f"Database verification:")
        logger.info(f"Number of documents: {vectorstore._collection.count()}")
        
        if results:
            sample_doc = results[0]
            logger.info("Sample document metadata:")
            logger.info(f"Source: {sample_doc.metadata.get('source', 'No source')}")
            logger.info(f"Page: {sample_doc.metadata.get('page', 'No page')}")
            logger.info(f"Content preview: {sample_doc.page_content[:100]}...")
        
        return True
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False

def main():
    try:
        # Define files and directories
        files = [
            "Lecture 1_slides-combined.pdf",
            "Network_security_text_book.pdf"
        ]
        persist_directory = 'database2'  # Changed to database2 to match server

        logger.info("Starting document processing")
        
        # Process all files
        all_splits = []
        for file_path in files:
            try:
                splits = load_and_split_document(file_path)
                all_splits.extend(splits)
                logger.info(f"Successfully processed {file_path}")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue

        if not all_splits:
            raise ValueError("No documents were successfully processed")

        logger.info(f"Total number of splits across all documents: {len(all_splits)}")

        # Initialize embeddings
        embeddings = getEmbeddings()

        # Create and persist vector store
        logger.info("Creating vector store...")
        vectorstore = Chroma.from_documents(
            documents=all_splits,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
        # Persist the database
        vectorstore.persist()
        logger.info(f"Vector store persisted to {persist_directory}")

        # Verify the database
        if verify_database(vectorstore):
            logger.info("Database verification successful")
        else:
            logger.warning("Database verification failed")

    except Exception as e:
        logger.error(f"An error occurred during vectorization: {str(e)}")
        raise

if __name__ == "__main__":
    main()