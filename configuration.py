from qdrant_client import QdrantClient
from pymongo import MongoClient


from dotenv import load_dotenv
load_dotenv()

client_mongo = MongoClient("mongodb://localhost:27017/")
my_db = client_mongo["RAG_Chat_System"]
my_logging = my_db["logs"]
my_memory = my_db["chatmemory"]


client = QdrantClient(url="https://2499f1af-a621-474e-9ebc-82a4fbd88b14.eu-west-1-0.aws.cloud.qdrant.io",
                      api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.8wbxLG5fw36E6bZIlwrZEdI8VzKy-njrS7zzGs75vok",timeout=30)

api = my_logging.find_one({"name_api":"GEMINI_API_KEY"}).get("api_key")
print(api)