import openai
import os
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class EmbeddingHandler:
    def __init__(self):
        self.cache = {}
        # Load the SBERT model (you can choose any model, like "all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

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
