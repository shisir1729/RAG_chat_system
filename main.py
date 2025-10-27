from fastapi import FastAPI,HTTPException,UploadFile,File
from llama_index.core  import SimpleDirectoryReader,StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from models.models_document import logging
from configuration import my_logging,my_memory
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core import Document,VectorStoreIndex,Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from configuration import client
from llama_index.llms.gemini import Gemini
from google.generativeai.types import FunctionDeclaration,Tool
import google.generativeai as genai 
from google.generativeai.types import content_types        
genai.configure(api_key=my_logging.find_one({"name_api":"GEMINI_API_KEY"}).get("api_key"))

import tempfile
import os
import shutil
import json
from datetime import datetime

app = FastAPI()


def uplode_doc(file):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file.filename)
        

        # Save uploaded file to temp dir
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load document
        reader = SimpleDirectoryReader(input_dir=temp_dir)
        documents = reader.load_data()
        return documents[:20]
    
def retriever_tool(query:str,top_k:int):
        Settings.embed_model = GoogleGenAIEmbedding(model_name="gemini-embedding-001",api_key=my_logging.find_one({"name_api":"GEMINI_API_KEY"}).get("api_key"),embed_batch_size=6)
        qdrant_store = QdrantVectorStore(
            client=client,
            collection_name="chunks_data"
        )

        index = VectorStoreIndex.from_vector_store(qdrant_store)
        llm = Gemini(model="gemini-2.0-flash")

        query_engine= index.as_query_engine(llm = llm,similarity_top_k=top_k)
        response = query_engine.query(query)
   
        context_text = "\n\n".join([node.node.get_content() for node in response.source_nodes])
        return {"context":context_text}

def load_chat_history():
    """Load chat history from MongoDB"""

    chat_cursor = my_memory.find().sort("timestamp", -1).limit(5)
    chat_docs = list(chat_cursor)
    chat_docs.reverse()

    previous_messages = []

    for doc in chat_docs:
        if doc.get('user_query'):
            previous_messages.append({
                "role": "user",
                "parts": [doc['user_query']]
            })

        if doc.get('llm_response'):
            previous_messages.append({
                "role": "model",
                "parts": [doc['llm_response']]
            })

    return previous_messages

def save_to_history(user_query: str, llm_response: str):
    """Save conversation to MongoDB"""
    my_memory.insert_one({
        
        "user_query": user_query,
        "llm_response": llm_response,
        "timestamp": datetime.now()
        
    })
       
@app.get("/")
def info():
    return f"wellcome to the rag_system"



@app.post("/logging_api")
def logging_api(log:logging):
    api_data = log.model_dump()
    result = my_logging.insert_one(api_data)

    return{"status_code":200,"id":str(result.inserted_id)}



@app.post("/delete") 
def deleteon():
    

    client.delete_collection(collection_name="chunks_data")
    return(f"collection is delete")
    

@app.post("/upload")
def splitter_doc(file: UploadFile = File(...)):
    documents = uplode_doc(file)

    metadata_splitter = SentenceSplitter(
        chunk_size=3000,
        chunk_overlap=1000,
        include_metadata=False,
    )

    split_docs = []
    for doc in documents:
        nodes = metadata_splitter.get_nodes_from_documents([doc])
        split_docs.extend(
            [Document(text=node.text, metadata=node.metadata) for node in nodes]
        )
    
    embed_model = GoogleGenAIEmbedding(model_name="gemini-embedding-001",api_key=my_logging.find_one({"name_api":"GEMINI_API_KEY"}).get("api_key"),embed_batch_size=6)

    qdrant_store = QdrantVectorStore(client=client,collection_name="chunks_data")
    storage_context1 = StorageContext.from_defaults(vector_store=qdrant_store)
    VectorStoreIndex.from_documents(
    split_docs,
    embed_model=embed_model,
    storage_context=storage_context1
       )

    if documents:
        return {"message": f"{file.filename} processed successfully"}
    else:
        return {"message": "No documents were loaded from the file."}    


@app.post("/query/{query}")
def query(query:str):
    #retriever_text = retriever_tool(query) 
    chat_history_text = load_chat_history()
    #print(chat_history_text)
    #print(type(retriever_text))
    retriever_function = FunctionDeclaration(
       name="retriever_text",
       description="""
                Retrieves relevant documents for user queries.
                 """,
       parameters={
         "type": "object",
            "properties": {
                
            "query": {
                "type": "string",
                "description": "search query or question"
                },
            "top_k": {
                "type": "integer",
                "description": "The number of top relevant passages to retrieve. Defaults to 3",
                
                }
        },
        "required": ["query","top_k"]
       }
    )
    system_instruction = """You are a helpful AI assistant to answer user questions from availabe tools.
                            Do not rely on your own kneoledge use retriever_text for all  kind of facts.
                            use retriever_text tool for retriving the fact and a details for the user request query  .
                            If you still can’t find the answer after using the tools, politely say:
                                    “I’m sorry, I couldn’t find the answer.”

                            Guidelines:

                                -Respond clearly, concisely, and helpfully.
                                -Maintain a polite and professional tone in all responses.
                   """

    model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    system_instruction=system_instruction,
    tools=[Tool(function_declarations=[retriever_function])]
     )
    
    chat = model.start_chat(history=chat_history_text,enable_automatic_function_calling=True)
    print(chat)
    print("---------------------chat _--------------------------------------")
    response = chat.send_message(query)
    print(response)
    print("------------------response -------------------------------")
    function_call_text = response.candidates[0].content.parts[0].text
    print(function_call_text)
    print("-----------------------------functon call text ---------------")

    function_call = response.candidates[0].content.parts[0]
    print(function_call)
    print("----------------functioncall name-----------------------")
    function_handlers = {"retriever_text":retriever_tool}
    print(function_handlers)
    # print("---------------------function handlears -----------------------------")
    while True:
        parts = response.candidates[0].content.parts

    # Collect all function calls in this turn
        function_calls = [p.function_call for p in parts if getattr(p, "function_call", None)]

        if function_calls:
            function_responses = []
            for fc in function_calls:
                # execute the function
                result = function_handlers[fc.name](**dict(fc.args))
                
                function_responses.append({
                    "function_response": {
                        "name": fc.name,
                        "response": result
                    }
                })

            # Send ALL function responses back at once
            chat_response = chat.send_message(
                content_types.to_content({
                    "role": "function",
                    "parts": function_responses
                })
            )

            response_text = chat_response.text
            save_to_history(query, response_text)
            return response_text

        else:
            # No function call → just return text
            response_text = response.text
            save_to_history(query, response_text)
            return response_text

        
            
        
    


  
















    



    
   
    



    
    

    

