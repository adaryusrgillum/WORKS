import chromadb
import os

def check():
    if os.path.exists("./chroma_db"):
        client = chromadb.PersistentClient(path="./chroma_db")
        try:
            collection = client.get_collection("seobot_knowledge")
            print(f"seobot_knowledge (./chroma_db): {collection.count()}")
        except Exception:
            print("seobot_knowledge not found in ./chroma_db")
    else:
        print("./chroma_db does not exist")

    if os.path.exists("./seo_vector_db"):
        client = chromadb.PersistentClient(path="./seo_vector_db")
        try:
            collection = client.get_collection("seo_knowledge")
            print(f"seo_knowledge (./seo_vector_db): {collection.count()}")
        except Exception:
            print("seo_knowledge not found in ./seo_vector_db")
    else:
        print("./seo_vector_db does not exist")

if __name__ == "__main__":
    check()
