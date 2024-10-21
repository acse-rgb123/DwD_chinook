import openai
import os
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingHandler:
    def __init__(self):
        self.cache = {}

    def get_embedding(self, text):
        if text in self.cache:
            return self.cache[text]
        
        # Ensure that 'text' is passed as a string and not a list
        embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")['data'][0]['embedding']
        self.cache[text] = embedding
        return embedding

    def get_embeddings_batch(self, texts):
        texts_to_embed = [text for text in texts if text not in self.cache]
        if texts_to_embed:
            embeddings = openai.Embedding.create(input=texts_to_embed, model="text-embedding-ada-002")['data']
            for text, embedding in zip(texts_to_embed, embeddings):
                self.cache[text] = embedding['embedding']

        return [self.cache[text] for text in texts]

    def calculate_similarity(self, embedding1, embedding2):
        return cosine_similarity([embedding1], [embedding2])[0][0]
