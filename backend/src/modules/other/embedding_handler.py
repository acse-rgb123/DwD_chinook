import os
import numpy as np
import torch
from transformers import RobertaTokenizer, RobertaModel
from sklearn.metrics.pairwise import cosine_similarity
import faiss


class EmbeddingHandler:
    def __init__(
        self,
        model_name="sentence-transformers/roberta-base-nli-stsb-mean-tokens",
        output_dir="./output",
        schema=None,
    ):
        self.cache = {}
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = RobertaModel.from_pretrained(model_name)
        self.output_dir = output_dir
        self.schema = schema  # Store schema information here
        os.makedirs(self.output_dir, exist_ok=True)

    def get_combined_embedding(self, text, context=None):
        """Generate an embedding that includes optional context, e.g., documentation."""
        combined_text = f"{text} {context}" if context else text
        return self.get_embedding(combined_text)

    def get_embedding(self, text):
        """Retrieve or generate an embedding for a single text entry using RoBERTa."""
        if text in self.cache:
            return self.cache[text]

        # Tokenize and generate embeddings using RoBERTa
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        self.cache[text] = embedding
        return embedding

    def get_embeddings_batch(self, texts, context=None):
        """Batch embedding with optional context added to each entry."""
        embeddings = []
        for text in texts:
            combined_text = f"{text} {context}" if context else text
            embedding = self.get_embedding(combined_text)
            embeddings.append(embedding)
        return embeddings

    def calculate_similarity(self, embedding1, embedding2):
        """Compute cosine similarity between two embeddings and apply threshold."""
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        return similarity

    # Saving and loading embeddings
    def save_embeddings(self, embeddings, file_name="embeddings.npy"):
        file_path = os.path.join(self.output_dir, file_name)
        np.save(file_path, embeddings)
        print(f"Embeddings saved to {file_path}")

    def load_embeddings(self, file_name="embeddings.npy"):
        file_path = os.path.join(self.output_dir, file_name)
        embeddings = np.load(file_path)
        return embeddings

    # FAISS Indexing methods
    def save_faiss_index(self, embeddings, file_name="faiss_index.faiss"):
        """Create and save FAISS index."""
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        file_path = os.path.join(self.output_dir, file_name)
        faiss.write_index(index, file_path)
        print(f"FAISS index saved to {file_path}")

    def load_faiss_index(self, file_name="faiss_index.faiss"):
        file_path = os.path.join(self.output_dir, file_name)
        index = faiss.read_index(file_path)
        return index
