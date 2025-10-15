from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Document(BaseModel):
    file_name:str
    author:str
    document_type:str
    data_create:datetime




class Splitter(BaseModel):
    chunk_size:int =512
    chunk_overlap:int=50
    includ_metadata : bool=True


class logging(BaseModel):
    api_name:str
    api_key:str
    timestamp:datetime


class Chat_history(BaseModel):
    user_query:str
    llm_response:str



