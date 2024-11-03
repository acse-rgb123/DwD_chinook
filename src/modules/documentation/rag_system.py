import pandas as pd

class RAGSystem:
    def __init__(self, embedding_handler, documentation):
        self.embedding_handler = embedding_handler
        self.documentation = documentation
        self.doc_chunks, self.chunk_embeddings = self.process_and_embed_documentation()

    def process_and_embed_documentation(self):
        doc_chunks = {}
        chunk_embeddings = {}

        print("Flattening and chunking documentation sections...")
        
        for doc_key, doc_text in self.documentation.items():
            if not doc_text.strip():
                print(f"Warning: Empty document text for section '{doc_key}'. Skipping.")
                continue

            print(f"Processing section '{doc_key}' - Length: {len(doc_text)} characters")
            
            # Apply fixed-size chunking with 100 words per chunk
            sections = self.chunk_document(doc_text, max_chunk_size=100)
            for i, section in enumerate(sections):
                chunk_key = f"{doc_key}_chunk_{i}"
                doc_chunks[chunk_key] = section
                # Embed each chunk
                chunk_embeddings[chunk_key] = self.embedding_handler.get_embedding(section)
                print(f"Embedded Chunk: {chunk_key} - Content: '{section[:50]}...'")  # Print first 50 chars of each chunk
            
        print("Completed embedding documentation chunks.")
        print(f"Total Chunks Created: {len(doc_chunks)}")
        
        return doc_chunks, chunk_embeddings

    def chunk_document(self, text, max_chunk_size=100):
        # Split text into chunks of max_chunk_size words
        words = text.split()
        chunks = []
        
        # Iterate over words in increments of max_chunk_size
        for i in range(0, len(words), max_chunk_size):
            chunk = " ".join(words[i:i + max_chunk_size])  # Join every 100 words into a chunk
            chunks.append(chunk)
        
        print(f"Document split into {len(chunks)} chunks.")
        for idx, chunk in enumerate(chunks[:5]):  # Print the first 5 chunks as a sample
            print(f"Chunk {idx+1}: {chunk[:100]}...")  # Print first 100 chars of each chunk
        
        return chunks

    import pandas as pd

    def retrieve_relevant_docs(self, query, similarity_threshold=0.45):
        """
        Retrieve relevant document chunks based on similarity to the user query.
        
        Parameters:
        - query (str): The user query to find relevant document chunks for.
        - similarity_threshold (float): Minimum similarity score for a chunk to be considered relevant.
        
        Returns:
        - list: Relevant document chunks above the similarity threshold.
        """
        # Embed the query for comparison with documentation chunks
        query_embedding = self.embedding_handler.get_embedding(query)
        similarities = []

        # Compare query embedding to each chunk embedding
        print("Calculating similarities between query and document chunks...")
        for chunk_key, chunk_embedding in self.chunk_embeddings.items():
            similarity = self.embedding_handler.calculate_similarity(query_embedding, chunk_embedding)
            chunk_content = self.doc_chunks[chunk_key]  # Retrieve the actual content of the chunk
            similarities.append((chunk_key, similarity, chunk_content))
            print(f"Similarity with {chunk_key}: {similarity}")  # Debugging output for each similarity score

        # Sort chunks by similarity score and select top 10
        sorted_chunks = sorted(similarities, key=lambda x: x[1], reverse=True)
        top_chunks = [(chunk_key, similarity, chunk_content) for chunk_key, similarity, chunk_content in sorted_chunks if similarity >= similarity_threshold]

        if not top_chunks:
            print("No chunks found above the similarity threshold.")
            return []

        # Format the output in a structured DataFrame for clear display
        print("\nTop 10 Similarity Scoring Chunks:")
        top_chunks_df = pd.DataFrame(top_chunks[:10], columns=["Chunk Key", "Similarity Score", "Chunk Content"])
        top_chunks_df["Chunk Content"] = top_chunks_df["Chunk Content"].apply(lambda x: x[:200] + "..." if len(x) > 200 else x)

        # Print the table in markdown format for clearer visibility in outputs
        print(top_chunks_df.to_markdown(index=False, tablefmt="pipe"))

        # Return only the content of relevant chunks
        relevant_chunks = [chunk_content for _, similarity, chunk_content in top_chunks]

        return relevant_chunks

