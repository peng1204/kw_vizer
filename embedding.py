from chromadb.api.types import EmbeddingFunction
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
import torch

class MySentenceEmbedding(EmbeddingFunction):
    def __init__(self, model_id="distilbert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModel.from_pretrained(model_id)

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, dim=1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def __call__(self, input):
        embeddings = []
        for text in input:
            encoded_input = self.tokenizer(text, padding=True, truncation=True, return_tensors='pt')
            with torch.no_grad():
                model_output = self.model(**encoded_input)
            sentence_embedding = self._mean_pooling(model_output, encoded_input['attention_mask'])
            sentence_embedding = F.normalize(sentence_embedding, p=2, dim=1)
            embeddings.append(sentence_embedding[0].tolist())
        return embeddings

# 인스턴스 생성
get_sentence_embedding = MySentenceEmbedding()
