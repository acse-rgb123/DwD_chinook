import os

class RAGSystem:
    def __init__(self, embedding_handler, documentation):
        self.embedding_handler = embedding_handler
        self.documentation = documentation
        self.doc_embeddings = self.embed_documentation()

    def embed_documentation(self):
        doc_embeddings = {}
        for doc_key, doc_text in self.documentation.items():
            doc_embeddings[doc_key] = self.embedding_handler.get_embedding(doc_text)
        return doc_embeddings

    def retrieve_relevant_docs(self, query, similarity_threshold=0.75):
        query_embedding = self.embedding_handler.get_embedding(query)
        similarities = []
        for doc_key, doc_embedding in self.doc_embeddings.items():
            similarity = self.embedding_handler.calculate_similarity(query_embedding, doc_embedding)
            similarities.append((doc_key, similarity))

        # Filter documents based on the similarity threshold
        relevant_docs = [doc_key for doc_key, similarity in similarities if similarity >= similarity_threshold]

        print(f"Retrieved relevant documents based on similarity threshold of {similarity_threshold}:")
        for doc in relevant_docs:
            print(doc)

        return relevant_docs

