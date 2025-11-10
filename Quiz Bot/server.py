import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import ollama
import chromadb
from flask import Flask
from flask_cors import CORS
from flask import request, jsonify

app = Flask(__name__)
CORS(app)
# def getEmbeddings():
#     return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# def setup_chroma():
#     # Initialize ChromaDB client
#     db=Chroma(persist_directory='database2', embedding_function=getEmbeddings())
    
#     return db

# def query_documents(db, query, n_results=2):
#     # Query the collection
#     results = db.similarity_search(query, k=n_results)
    
#     # Extract and join the retrieved chunks
#     context = "\n".join([result.page_content for result in results])
#     return context

# def generate_prompt(query, context):
#     # Create a prompt template that includes context and query
#     prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
#     I am providing you prompt from user who is a professor of university and context. I want you to contruct a quiz from the provided context that contains only 2 open-ended questions.
#     question with their answers.

#     Context: {context}

#     User: {query}
#     Chatbot:"""
#     return prompt

# def get_ollama_response(prompt):
#     # Generate response using llama3 through Ollama
#     response = ollama.chat(
#         model='llama3',
#         messages=[
#             {
#                 'role': 'user',
#                 'content': prompt
#             }
#         ]
#     )
#     return response['message']['content']



# app = Flask(__name__)
# CORS(app)

# @app.route('/open-ended', methods=['POST'])
# def process_chat():
#     try:
#         # Get data from request
#         data = request.get_json()
#         user_query = data.get('query')
#         n_qs = data.get('qs', 2)  # Default to 2 if not specified
        
#         # Setup ChromaDB
#         db = setup_chroma()
        
#         # Query relevant documents
#         context = query_documents(db, user_query, 10)
        
#         # Generate prompt with context
#         full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
#         I am providing you prompt from user who is a professor of university and context. I want you to contruct {n_qs} open-ended questions for quiz from the provided context with answers.

#         Context: {context}

#         User: {user_query}
#         Chatbot:"""
        
#         # Get response from Ollama
#         response = get_ollama_response(full_prompt)
        
#         return jsonify({
#             'response': response,
#             'status': 'success'
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': str(e),
#             'status': 'error'
#         }), 500
    
# @app.route('/mcqs', methods=['POST'])
# def mcqs():
#     try:
#         # Get data from request
#         data = request.get_json()
#         user_query = data.get('query')
#         n_qs = data.get('qs', 2)  # Default to 2 if not specified
        
#         # Setup ChromaDB
#         db = setup_chroma()
        
#         # Query relevant documents
#         context = query_documents(db, user_query, 10)
        
#         # Generate prompt with context
#         full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
#         I am providing you prompt from user who is a professor of university and context. I want you to contruct {n_qs} multiple choice questions each having 4 options for quiz from the provided context with answers.
        
#         Context: {context}

#         User: {user_query}
#         Chatbot:"""
        
#         # Get response from Ollama
#         response = get_ollama_response(full_prompt)
        
#         return jsonify({
#             'response': response,
#             'status': 'success'
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': str(e),
#             'status': 'error'
#         }), 500
    


# @app.route('/true-false', methods=['POST'])
# def true_false():
#     try:
#         # Get data from request
#         data = request.get_json()
#         user_query = data.get('query')
#         n_qs = data.get('qs', 2)  # Default to 2 if not specified
        
#         # Setup ChromaDB
#         db = setup_chroma()
        
#         # Query relevant documents
#         context = query_documents(db, user_query, 10)
        
#         # Generate prompt with context
#         full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
#         I am providing you prompt from user who is a professor of university and context. I want you to contruct {n_qs} true/false questions for quiz from the provided context with answers.

#         Context: {context}

#         User: {user_query}
#         Chatbot:"""
        
#         # Get response from Ollama
#         response = get_ollama_response(full_prompt)
#         # console.log(response)
#         print(response)
#         return jsonify({
#             'response': response,
#             'status': 'success'
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': str(e),
#             'status': 'error'
#         }), 500

# if __name__ == "__main__":
#     app.run(debug=True)
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import ollama
import chromadb
from flask import Flask
from flask_cors import CORS
from flask import request, jsonify


def getEmbeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def setup_chroma():
    try:
        # Initialize ChromaDB client with explicit settings
        db = Chroma(
            persist_directory='database2',
            embedding_function=getEmbeddings(),
            collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity for better matching
        )
        return db
    except Exception as e:
        print(f"Error setting up ChromaDB: {str(e)}")
        raise

def query_documents(db, query, n_results=2):
    # Query the collection
    try:
        results = db.similarity_search(query, k=n_results)
        
        # Extract content and metadata
        contexts = []
        for result in results:
            source_info = {
                'content': result.page_content,
                'source': result.metadata.get('source', 'Unknown source'),
                'page': result.metadata.get('page', 'Unknown page')
            }
            contexts.append(source_info)
        
        return contexts
    except Exception as e:
        print(f"Error in query_documents: {str(e)}")
        return []

def get_ollama_response(prompt):
    # Generate response using llama3 through Ollama
    response = ollama.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )
    return response['message']['content']

def format_context_with_sources(contexts):
    # Format context with source information
    formatted_contexts = []
    for ctx in contexts:
        formatted_context = f"""
Content from {ctx['source']} (Page {ctx['page']}):
{ctx['content']}
---"""
        formatted_contexts.append(formatted_context)
    return "\n".join(formatted_contexts)

@app.route('/open-ended', methods=['POST'])
def process_chat():
    try:
        data = request.get_json()
        user_query = data.get('query')
        n_qs = data.get('qs', 2)
        
        db = setup_chroma()
        contexts = query_documents(db, user_query, 10)
        formatted_context = format_context_with_sources(contexts)
        
        full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
        I am providing you prompt from user who is a professor of university and context. I want you to construct {n_qs} open-ended questions for quiz from the provided context with answers.
        
        For each question, please include the source information (document name and page number) from where the information was taken.
        Format your response as follows for each question:

        Question [Source: <document_name>, Page: <page_number>]: <question_text>
        Answer: <answer_text>

        Context: {formatted_context}

        User: {user_query}
        Chatbot:"""
        
        response = get_ollama_response(full_prompt)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/mcqs', methods=['POST'])
def mcqs():
    try:
        data = request.get_json()
        user_query = data.get('query')
        n_qs = data.get('qs', 2)
        
        db = setup_chroma()
        contexts = query_documents(db, user_query, 10)  # Get more context to ensure sufficient material
        
        if not contexts:
            return jsonify({
                'error': 'No relevant content found in the database',
                'status': 'error'
            }), 404
        
        formatted_context = format_context_with_sources(contexts)
        
        full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
        I am providing you with specific context from our course materials. You MUST ONLY generate questions based on the provided context below. Do not use any information outside of this context.
        
        I want you to construct {n_qs} multiple choice questions with 4 options for a quiz. Each question must come directly from the context provided.
        
        Rules:
        1. ONLY use information from the provided context
        2. Each question must include the exact source document and page number from where it was taken
        3. Ensure the correct answer is present in the options
        4. All distractors (wrong options) should be plausible and related to the topic
        
        Format your response exactly as follows for each question:

        Question [Source: <document_name>, Page: <page_number>]: <question_text>
        A) <option_text>
        B) <option_text>
        C) <option_text>
        D) <option_text>
        Answer: <correct_option>

        Context:
        {formatted_context}

        User Query: {user_query}

        Remember: Only create questions from the information explicitly stated in the above context. Do not include any external knowledge.
        """
        
        # Debug: Print the context being used
        print("Formatted Context:", formatted_context)
        
        response = get_ollama_response(full_prompt)
        print(response)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in mcqs endpoint: {str(e)}")  # Debug: Print the error
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
# def mcqs():
#     try:
#         data = request.get_json()
#         user_query = data.get('query')
#         n_qs = data.get('qs', 2)
        
#         db = setup_chroma()
#         context = query_documents(db, user_query, 10)
#         formatted_context = format_context_with_sources(context)
        
#         full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
#         I am providing you prompt from user who is a professor of university and context. I want you to construct {n_qs} multiple choice questions each having 4 options for quiz from the provided context with answers.
        
#         For each question, please include the source information (document name and page number) from where the information was taken.
#         Format your response as follows for each question:

#         Question [Source: <document_name>, Page: <page_number>]: <question_text>
#         A) <option_text>
#         B) <option_text>
#         C) <option_text>
#         D) <option_text>
#         Answer: <correct_option>

#         Context: {formatted_context}

#         User: {user_query}
#         Chatbot:"""
        
#         response = get_ollama_response(full_prompt)
        
#         return jsonify({
#             'response': response,
#             'status': 'success'
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': str(e),
#             'status': 'error'
#         }), 500

@app.route('/true-false', methods=['POST'])
def true_false():
    try:
        data = request.get_json()
        user_query = data.get('query')
        n_qs = data.get('qs', 2)
        
        db = setup_chroma()
        contexts = query_documents(db, user_query, 10)
        formatted_context = format_context_with_sources(contexts)
        
        full_prompt = f"""You are a chatbot that specializes in computer network, security and communication. Your tone should be professional and informative.
        I am providing you prompt from user who is a professor of university and context. I want you to construct {n_qs} true/false questions for quiz from the provided context with answers.
        
        For each question, please include the source information (document name and page number) from where the information was taken.
        Format your response as follows for each question:

        Question [Source: <document_name>, Page: <page_number>]: <question_text>
        Answer: <True/False>

        Context: {formatted_context}

        User: {user_query}
        Chatbot:"""
        
        response = get_ollama_response(full_prompt)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
