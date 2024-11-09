import spacy
import torch
from transformers import RobertaTokenizer, RobertaModel
from sklearn.metrics.pairwise import cosine_similarity


class KeywordExtractor:
    def __init__(self, method="spacy"):
        self.method = method.lower()

        if self.method == "spacy":
            self.nlp = spacy.load("en_core_web_sm")
        elif self.method == "roberta":
            self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
            self.model = RobertaModel.from_pretrained(
                "roberta-base", add_pooling_layer=False
            )
        else:
            raise ValueError("Invalid method. Choose 'spacy' or 'roberta'.")

    def extract_keywords(self, query, similarity_threshold=0.3, window_size=2):
        if self.method == "spacy":
            return self.extract_with_spacy(query)
        elif self.method == "roberta":
            return self.extract_with_roberta(query, similarity_threshold, window_size)

    def extract_with_spacy(self, query):

        doc = self.nlp(query)
        keywords = set()

        # Extract named entities as keywords
        for ent in doc.ents:
            keywords.add(ent.text)

        # Extract noun chunks as keywords
        for chunk in doc.noun_chunks:
            keywords.add(chunk.text)

        return list(keywords)

    def extract_with_roberta(self, query, similarity_threshold, window_size):
        inputs = self.tokenizer(query, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            token_embeddings = outputs.last_hidden_state.squeeze(0)

        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        query_embedding = token_embeddings.mean(dim=0).unsqueeze(0)
        similarities = cosine_similarity(query_embedding, token_embeddings)

        # Extract keywords as individual tokens
        keywords = [
            tokens[i].replace("Ġ", "")
            for i, sim in enumerate(similarities[0])
            if sim >= similarity_threshold and tokens[i].isalpha()
        ]

        # Extract phrases using the specified window size
        phrases = []
        for i in range(len(tokens)):
            for window in range(2, window_size + 1):
                if i + window <= len(tokens):
                    phrase = " ".join(
                        [tokens[j].replace("Ġ", "") for j in range(i, i + window)]
                    )
                    phrase_embedding = token_embeddings[i : i + window].mean(dim=0)
                    phrase_similarity = cosine_similarity(
                        query_embedding, phrase_embedding.unsqueeze(0)
                    )[0][0]
                    if phrase_similarity >= similarity_threshold and all(
                        word.isalpha() for word in phrase.split()
                    ):
                        phrases.append(phrase)

        return list(set(keywords + phrases))
