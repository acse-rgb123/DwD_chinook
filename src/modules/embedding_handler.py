import os
import numpy as np
import openai
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import faiss

class EmbeddingHandler:
    def __init__(self, model_name='all-MiniLM-L6-v2', output_dir='./output'):
        self.cache = {}
        self.model = SentenceTransformer(model_name)
        self.output_dir = output_dir  # New output directory
        os.makedirs(self.output_dir, exist_ok=True)  # Ensure the directory exists

    def get_embedding(self, text):
        if text in self.cache:
            return self.cache[text]
        
        # Ensure 'text' is passed as a string, not a list
        embedding = self.model.encode(text, convert_to_tensor=False)
        self.cache[text] = embedding
        return embedding

    def get_embeddings_batch(self, texts):
        texts_to_embed = [text for text in texts if text not in self.cache]
        if texts_to_embed:
            embeddings = self.model.encode(texts_to_embed, convert_to_tensor=False)
            for text, embedding in zip(texts_to_embed, embeddings):
                self.cache[text] = embedding

        return [self.cache[text] for text in texts]

    def calculate_similarity(self, embedding1, embedding2):
        return cosine_similarity([embedding1], [embedding2])[0][0]

    # New method to save embeddings to a .npy file
    def save_embeddings(self, embeddings, file_name='embeddings.npy'):
        file_path = os.path.join(self.output_dir, file_name)
        np.save(file_path, embeddings)
        print(f"Embeddings saved to {file_path}")

    # New method to create and save FAISS index
    def save_faiss_index(self, embeddings, file_name='faiss_index.faiss'):
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        file_path = os.path.join(self.output_dir, file_name)
        faiss.write_index(index, file_path)
        print(f"FAISS index saved to {file_path}")

    # New method to load embeddings from a .npy file
    def load_embeddings(self, file_name='embeddings.npy'):
        file_path = os.path.join(self.output_dir, file_name)
        embeddings = np.load(file_path)
        return embeddings

    # New method to load FAISS index
    def load_faiss_index(self, file_name='faiss_index.faiss'):
        file_path = os.path.join(self.output_dir, file_name)
        index = faiss.read_index(file_path)
        return index


    def calculate_similarity(self, embedding1, embedding2):
        return cosine_similarity([embedding1], [embedding2])[0][0]
