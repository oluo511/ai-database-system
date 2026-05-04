import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(BASE_DIR, '..', 'data', 'rag', 'docs', 'project_group6.txt')

# LOAD THE MODEL (The "MVM" Choice)
# Local prototyping model. Small (~80MB) and fast
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_and_chunk_text(file_path, chunk_size=700, overlap=100):
    """
    Reads the document and breaks it into overlapping pieces.
    Overlap ensures we don't cut a sentence in half and lose context.
    """
    if not os.path.exists(file_path):
        return [f"ERROR: Could not find the file at {file_path}. Please check your data folder."]

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    chunks = []
    # SLIDING WINDOW: Moves forward by 600 chars (700 total minus 100 overlap)
    # for prototyping will probably switch to breaks to keep sections together
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks

def get_relevant_context(query, top_k=3):
    """
    Embeds the user query and converts text chunks to vectors 
    to find the most semantically relevant matches.
    """
    chunks = load_and_chunk_text(DOC_PATH)
    
    # Check if we actually got chunks (or an error message)
    if "ERROR" in chunks[0]:
        return chunks

    # VECTORIZATION (Turning text into 'meaning' coordinates)
    chunk_embeddings = model.encode(chunks)
    query_embedding = model.encode([query])
    
    # SIMILARITY SEARCH
    # This measures the mathematical 'angle' between the question and the chunks.
    similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

    # STATISTICAL ANALYSIS
    # top cosine similarity scores may have no difference between each other 
    # Z-scores explain how 'significant' each match is compared to the average
    mean_sim = np.mean(similarities)
    std_sim = np.std(similarities)
    
    # Calculate Z-Scores for all chunks
    # This tells us how many 'standard deviations' away from the average each match is
    z_scores = (similarities - mean_sim) / (std_sim + 1e-9) # Added tiny number to avoid div by zero
    
    # RANKING
    # Pick the top 'k' indices with the highest similarity scores
    # sort by similarity because order stays the same, Z-scores are for validation
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    # We return a list of dictionaries so we don't lose the "Confidence" data
    # Z-score > 2.0 high confidence
    # Z-score 1.0-2.0 medium confidence
    # Z-score < 1.0 low confidence
    results = []
    for i in top_indices:
        results.append({
            "text": chunks[i],
            "z_score": round(z_scores[i], 2),
            "similarity": round(similarities[i], 4)
        })
    
    return results

if __name__ == "__main__":
    # LOCAL TEST
    test_query = "Briefly summarize the SalesOrder table in the database"
    
    print(f"Running RAG search for: '{test_query}'...")
    results = get_relevant_context(test_query)
    
    print(f"\n--- Top {len(results)} matches found ---")
    for i, match in enumerate(results):
        # We access the 'text' key before slicing the first 300 characters
        # We also print the Z-score to verify the match confidence
        print(f"\n[Result {i+1}] (Z-Score: {match['z_score']}):")
        print(f"{match['text'][:300]}...")