import chromadb
client = chromadb.PersistentClient("chroma_db")
collection = client.get_collection("products")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
print(collection.query(model.encode(["dog food"])))