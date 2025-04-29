import os
import load_documents
from sentence_transformers import SentenceTransformer
import time
from tqdm import tqdm
import numpy as np
import faiss
import pickle

def build_vector_store():
    print("\n=== Starting Vector Store Creation with FAISS ===")
    
    # 1. Document Loading
    print("\n[1/5] Loading PDF documents...")
    folder_path = "source_pdfs"
    
    if not os.path.exists(folder_path):
        print(f"❌ Error: PDF folder not found at {folder_path}")
        return
    
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"❌ Error: No PDF files found in {folder_path}")
        return
    
    print(f"Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file}")

    # Load documents with metadata tracking
    documents = []
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            file_path = os.path.join(folder_path, pdf_file)
            text = load_documents.load_pdf(file_path)  # Assuming you have this function
            documents.append({
                "text": text,
                "source": pdf_file,
                "pages": "all"  # Or track specific pages if needed
            })
        except Exception as e:
            print(f"⚠️ Error loading {pdf_file}: {str(e)}")
            continue

    if not documents:
        print("❌ No documents were successfully loaded")
        return
    
    combined_text = "\n\n".join([doc["text"] for doc in documents])
    print(f"✓ Loaded {len(documents)} PDFs with {len(combined_text)} total characters")

    # 2. Text Chunking with metadata preservation
    print("\n[2/5] Creating text chunks...")
    chunk_size = 500
    chunks = []
    chunk_metadata = []
    
    for doc in documents:
        text = doc["text"]
        source = doc["source"]
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            chunks.append(chunk)
            chunk_metadata.append({
                "source": source,
                "chunk_id": f"{source}_chunk_{len(chunks)}",
                "page_range": doc.get("pages", "all")
            })
    
    print(f"✓ Created {len(chunks)} chunks ({chunk_size} chars each)")
    print(f"Sample chunk metadata: {chunk_metadata[0]}")

    # 3. Initialize Embedding Model
    print("\n[3/5] Loading embedding model...")
    model_name = 'all-MiniLM-L6-v2'
    try:
        embedder = SentenceTransformer(model_name)
        print(f"✓ Model '{model_name}' loaded")
        test_embedding = embedder.encode("test")
        embedding_dim = len(test_embedding)
        print(f"Vector dimension: {embedding_dim}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    # 4. Create FAISS Index
    print("\n[4/5] Creating FAISS index...")
    try:
        # Create FlatIP index with ID mapping
        index = faiss.IndexFlatIP(embedding_dim)
        index = faiss.IndexIDMap2(index)
        
        # Generate embeddings with progress tracking
        print("Generating embeddings...")
        embeddings = []
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
            embedding = embedder.encode(chunk, normalize_embeddings=True)
            embeddings.append(embedding)
        
        # Convert to numpy array
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to index with IDs
        ids = np.arange(len(chunks)).astype('int64')
        index.add_with_ids(embeddings, ids)
        
        print(f"✓ FAISS index created with {index.ntotal} vectors")
    except Exception as e:
        print(f"❌ Failed to create FAISS index: {e}")
        return

    # 5. Save FAISS Index and Metadata
    print("\n[5/5] Saving vector store...")
    save_dir = "faiss_store"
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        # Save FAISS index
        faiss.write_index(index, os.path.join(save_dir, "index.faiss"))
        
        # Save metadata with chunk mapping
        metadata = {
            "chunks": chunks,
            "metadata": chunk_metadata,
            "document_sources": [doc["source"] for doc in documents],
            "embedding_model": model_name,
            "creation_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(os.path.join(save_dir, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f)
        
        print(f"✓ Vector store saved to {save_dir}")
    except Exception as e:
        print(f"❌ Failed to save vector store: {e}")
        return

    # Results Summary
    print("\n=== Results ===")
    print(f"Total PDFs processed: {len(documents)}")
    print(f"Total chunks created: {len(chunks)}")
    print(f"Vector dimension: {embedding_dim}")
    print(f"Index size: {index.ntotal} vectors")
    
    print("\n✅ FAISS vector store created successfully!")

    return {
        "documents_processed": len(documents),
        "total_chunks": len(chunks),
        "embedding_dim": embedding_dim,
        "index_size": index.ntotal,
        "storage_path": save_dir
    }

if __name__ == "__main__":
    start_time = time.time()
    print("Starting FAISS vector store creation...")
    
    result = build_vector_store()
    
    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")